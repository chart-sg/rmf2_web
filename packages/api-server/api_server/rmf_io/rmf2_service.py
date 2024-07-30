import asyncio
import json
import uuid
from asyncio import Future
from typing import Callable, Dict, Optional
from uuid import uuid4

import rclpy
import rclpy.node
import rclpy.qos
import reactivex as rx
from fastapi import HTTPException
from reactivex.subject import BehaviorSubject
from rmf_task_msgs.msg import ApiRequest, ApiResponse
from tortoise.contrib.pydantic.base import PydanticModel

from api_server import models as mdl
from api_server.logger import logger
from api_server.models import FleetState, TaskState

# from api_server.repositories import AlertRepository, TaskRepository
from api_server.repositories import alert_repo_dep
from api_server.rmf_io import alert_events, fleet_events, task_events
from api_server.rmf_io.rmf_service import tasks_service
from api_server.rmf_io.state_monitor import stateMonitor
from api_server.ros import ros_node as default_ros_node
from api_server.util.rmf_task_builder import rmfTaskBuilder

user: mdl.User = mdl.User(username="__rmf_internal__", is_admin=True)
alert_repo = alert_repo_dep(user)


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class ServiceSequence:
    """
    An abstract class containing the task,
    the start and end conditions,
    and notifications assigned to it
    """

    def __init__(self, name: str, startCondition=None, endCondition=None):
        self.name = name
        self.sm = stateMonitor()
        self.startCondition = startCondition
        self.endCondition = endCondition
        self.next_task = None
        self.fail_task = None
        self.out_data = {}
        self.complete_event = asyncio.Event()

    async def process_next(self, status: str = "pass"):

        # self.out_data = {"task_id": self.task_id}

        if status == "pass":
            if self.next_task:
                if isinstance(self.next_task, list):
                    await asyncio.gather(*(task.start() for task in self.next_task))
                else:
                    await self.next_task.start()
        elif status == "fail":
            if self.fail_task:
                if isinstance(self.fail_task, list):
                    await asyncio.gather(*(task.start() for task in self.fail_task))
                else:
                    await self.fail_task.start()

    async def start(self):
        # await self.process_next()
        pass

    async def stop(self):
        pass

    async def pause(self):
        pass

    async def resume(self):
        pass

    async def onComplete(self):
        if self.next_task:
            if isinstance(self.next_task, list):
                await asyncio.gather(*(task.start() for task in self.next_task))
            else:
                await self.next_task.start()

    async def onError(self):
        pass


class SequenceNotification(ServiceSequence):
    """
    Contains the body for a notification message,
    trigger condition, and whether it contains actionable actions
    for the user to perform on receiving the message
    """

    def __init__(
        self,
        name: str,
        userGroup: str,
        message: str = "",
        needAck: bool = False,
        messageAction=None,
        userId: str = None,
    ):
        super().__init__(name)
        self.user_id = userId
        self.user_group = userGroup
        self.message = message
        self.need_ack = needAck
        self.message_action = messageAction
        self.user_action = None

    async def handle_alert_update(self, alert: PydanticModel, alert_id: str):
        logger.warn(f"inside alert handler: {alert.original_id}")

        if alert.original_id == alert_id:
            action = self.sm.get_ack_status(alert)
            logger.warn(f"user action : {action}")

            if action in ["acknowledge", "accept"]:
                await self.onComplete()
            elif action in ["reject", "cancel"]:
                await self.onFail()
            else:
                pass  # alert is waiting for action

    async def start(self, start_data=None):
        if "task_id" in start_data and start_data["task_id"]:
            task_id = start_data["task_id"]
        else:
            task_id = str(uuid.uuid4())

        task_id = f"{self.name}-{task_id}"

        alert_new = await alert_repo.create_alert(
            alert_id=task_id,
            category="default",
            user_group=self.user_group,
            message=self.message,
            message_action=self.message_action,
        )

        if alert_new is not None:
            alert_events.alerts.on_next(alert_new)

        # if self.need_ack or self.message_action:

        # only if notif needs ack then we wait
        if self.need_ack:
            self.subscription = self.sm.alert.alerts.subscribe(
                lambda alert: asyncio.create_task(
                    self.handle_alert_update(alert, task_id)
                )
            )
            logger.info(f"lets wait for this {self.name} user action")

            await self.complete_event.wait()
            self.subscription.dispose()

        logger.info(f"Yaaaay! this {self.name} notification is completed!!")

        # else:
        #     # await asyncio.sleep(2)
        #     logger.info(
        #         f"Alert is not a robotic task id [{self.user_id}]: {self.message}"
        #     )


class SequenceCustom(ServiceSequence):
    """
    For other custom logic calls
    (i.e pushing data to HIT systems)
    """

    def __init__(self, name: str):
        super().__init__(name)

    async def start(self):
        logger.info(f"{self.name} task (custom) started")
        await asyncio.sleep(5)
        logger.info(f"{self.name} task (custom) completed")
        await self.process_next(status="pass")


class SequenceRoboticTask(ServiceSequence):
    """
    For RMF-related messages.
    (Used for robotics tasks)
    """

    def __init__(self, name: str, data={}):
        super().__init__(name)
        self.rmf_task_id: str
        self.task_id = ""
        self.data = data

    async def handle_task_update(
        self, task: TaskState, task_id: str, action: str, place: str
    ):
        # logger.warn(f"TaskUpdate: {task}")
        if task.booking.id == task_id:
            status = self.sm.get_task_action_status(task, action, place)

            if status in ["completed"]:
                await self.onComplete()
            elif status in ["failed", "canceled"]:
                await self.onFail()
            else:
                pass  # task still in progress

    async def onComplete(self):
        logger.info(f"{self.name} task (robotic) completed")
        self.complete_event.set()
        await self.process_next(status="pass")
        # if not self.end_condition_event.is_set():

    async def onFail(self):
        logger.info(f"{self.name} task (robotic) failed")
        self.complete_event.set()
        await self.process_next(status="fail")

    async def process_next(self, status: str = "pass"):

        self.out_data = {"task_id": self.task_id}
        if status == "pass":
            if self.next_task:
                if isinstance(self.next_task, list):
                    await asyncio.gather(
                        *(task.start(self.out_data) for task in self.next_task)
                    )
                else:
                    await self.next_task.start(self.out_data)
        elif status == "fail":
            if self.fail_task:
                if isinstance(self.fail_task, list):
                    await asyncio.gather(
                        *(task.start(self.out_data) for task in self.fail_task)
                    )
                else:
                    await self.fail_task.start(self.out_data)

    async def start(self, start_data=None):
        logger.info(f"{self.name} task (robotic) started")

        robot = self.data["robot"]
        fleet = self.data["fleet"]
        category = self.data["category"]
        place = self.data["start"]
        zoneType = self.data.get("zoneType", None)
        start = ""

        # if place is a function, call it
        if callable(place):
            start = place()
        else:
            start = place

        # payload = self.rmfTaskBuilder(**self.data)
        payload = rmfTaskBuilder(
            robot=robot, fleet=fleet, category=category, start=start, zoneType=zoneType
        )

        logger.info(f"RESPONSE: {payload}")

        resp = mdl.TaskDispatchResponse.parse_raw(await tasks_service().call(payload))

        # cancel workflow if request failed
        if not resp.__root__.success:
            raise RobotDispatchFailed(
                robot_id="aw", message=f"Failed to dispatch {robot} to {start}"
            )

        self.task_id = resp.__root__.state.booking.id

        # perform other tasks based on task status
        self.subscription = self.sm.task.task_states.subscribe(
            lambda task: asyncio.create_task(
                self.handle_task_update(task, self.task_id, "Go to", start)
            )
        )

        # Wait until the end_condition is set.
        logger.info(f"lets wait for this {self.name} task to be completed")
        await self.complete_event.wait()

        logger.info(f"Yaaaay! this {self.name} task is completed!!")
        self.subscription.dispose()


class Rmf2Service:
    """
    A module that allows for defining a ‘service’
    by grouping and chaining/sequencing multi-fleet robotic
    or automation tasks with notifications,
    with the use of configuration files.

    Main object containing ServiceSequences to run the tasks inside accordingly.
    """

    def __init__(self, name):
        self.name = name
        self.tasks = [ServiceSequence]
        self.status = None
        self.currentSequence = []
        self.data = {}
        self.loop = asyncio.AbstractEventLoop

    async def add_sequences_and_start(self, sequence):
        self.loop = asyncio.get_event_loop()
        self.status = "Running"
        # await sequence.start()
        task = self.loop.create_task(sequence.start())

        # await task
        logger.info(f"Yaaaay! service is completed!!")

        # old implementation
        # self.tasks.append(sequence)
        # asyncio.create_task(sequence.start())
        # await sequence.start()

    def stop(self):
        pass

    def pause(self):
        pass

    def getCurrentSequence(self):
        return [task.name for task in self.currentSequence]

    def skipSequence(self):
        pass

    def continue_(self):
        pass


if __name__ == "__main__":
    pass