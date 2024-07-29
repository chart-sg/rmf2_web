import asyncio
import json
import uuid
from asyncio import Future
from typing import Callable, Dict, Optional
from uuid import uuid4

import aiohttp
import rclpy
import rclpy.node
import rclpy.qos
import reactivex as rx
from fastapi import HTTPException
from reactivex.subject import BehaviorSubject
from rmf_task_msgs.msg import ApiRequest, ApiResponse
from tortoise.contrib.pydantic.base import PydanticModel

from api_server import models as mdl
from api_server.app_config import app_config
from api_server.gateway import rmf_gateway
from api_server.logger import logger
from api_server.models import FleetState, TaskState
from api_server.mqtt_client import mqtt_client, pudu_client

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

    def __init__(
        self, name: str, serviceId: str = None, startCondition=None, endCondition=None
    ):
        self.name = name
        self.sm = stateMonitor()
        self.startCondition = startCondition
        self.endCondition = endCondition
        self.service_id = serviceId
        self.next_task = None
        self.fail_task = None
        self.out_data = {}
        self.complete_event = asyncio.Event()

    async def set_context_info(self, data: Dict):
        for key, value in data.items():
            setattr(self, key, value)

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

    # async def set_service_id(self,service_id:str):
    #     self.service_id = service_id

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
        serviceId: str,
        userGroup: str,
        robotId: str = None,
        other: str = "",
        location: str = None,
        patientId: str = None,
        messageAction=None,
        userId: str = None,
        needAck: bool = False,
    ):
        super().__init__(name, serviceId)
        self.user_id = userId
        self.user_group = userGroup
        self.robot_id = robotId
        self.other = other
        self.location = location
        self.patient_id = patientId
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

        if (
            start_data is not None
            and isinstance(start_data, dict)
            and "task_id" in start_data
            and start_data["task_id"]
        ):
            task_id = start_data["task_id"]

        # if "task_id" in start_data and start_data["task_id"]:
        #     task_id = start_data["task_id"]
        else:
            task_id = str(uuid.uuid4())

        task_id = f"{self.name}-{task_id}"

        logger.info(f"{self.name} Notification, Service ID: {self.service_id}")

        alert_new = await alert_repo.create_alert(
            alert_id=task_id,
            category="default",
            robot_id=self.robot_id,
            service_id=self.service_id,
            location=self.location,
            alert_type=self.name,
            patient_id=self.patient_id,
            other=self.other,
            user_group=self.user_group,
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


class SequenceCustom(ServiceSequence):
    """
    For other custom logic calls
    (i.e pushing data to HIT systems)
    """

    def __init__(self, name: str, data=None, userGroup=None):
        super().__init__(name)
        self.data = data

    async def start(self):
        logger.info(f"{self.name} task (custom) started")
        await asyncio.sleep(5)
        logger.info(f"{self.name} task (custom) completed")
        # await self.process_next(status="pass")


class SequencePuduTask(ServiceSequence):
    """
    For Pudu mqtt calls
    (i.e calling pudu playsound)
    """

    def __init__(self, name: str, data=None, sequenceType=None, delay=0):
        super().__init__(name)
        self.data = data
        self.sequence_type = sequenceType
        self.delay = delay

    async def start(self):

        pudu_client().publish(f"/robot/playSound", json.dumps({"audio": "1"}))

        logger.info(f"Post sound delay is {self.delay } seconds!!")
        await asyncio.sleep(self.delay)
        logger.info(f"{self.name} task completed")


class SequenceTemiTask(ServiceSequence):
    """
    For Temi mqtt calls
    (i.e calling temi sequences systems)
    """

    def __init__(self, name: str, data=None, userGroup=None):
        super().__init__(name)
        self.data = data
        self.temi_id = self.data["temi_id"]
        self.sequence_type = self.data["sequence_type"]

    async def start(self):

        video_sequence = app_config.temi["video_sequence"]
        bed_exit_sequence = app_config.temi["bed_exit_sequence"]
        video_delay = app_config.delays["orientation_video"]
        responder_delay = app_config.delays["responder_delay"]

        delay = None

        if self.sequence_type == "video":
            sequence_id = video_sequence
            delay = video_delay
            mqtt_client().publish(
                f"temi/{self.temi_id}/command/sequence/play",
                json.dumps({"sequence_id": sequence_id}),
            )
        if self.sequence_type == "bed_exit":
            sequence_id = bed_exit_sequence
            delay = responder_delay
            mqtt_client().publish(
                f"temi/{self.temi_id}/command/sequence/play",
                json.dumps({"sequence_id": sequence_id}),
            )
        elif self.sequence_type == "pre_exit":
            delay = 0

            speech = "Bed Exit at Bed 2 detected. Attention. Please do not come out of the bed for your safety."
            jsonstr = {"utterance": speech}
            mqtt_client().publish(
                f"temi/{self.temi_id}/command/tts", json.dumps(jsonstr)
            )
        else:
            logger.error(f"Temi sequence {self.sequence_type} is unexpected!")

        # logger.info(f"{self.name} task started")

        logger.info(f"Temi task duration is {delay} seconds!!")
        await asyncio.sleep(delay)

        logger.info(f"{self.name} task completed")


class SequenceApiCall(ServiceSequence):
    """
    For GET API calls
    (i.e get setbuckle )
    """

    def __init__(self, name: str, data=None, userGroup=None):
        super().__init__(name)
        self.data = data

        self.url = self.data["url"]
        self.method = self.data["method"]
        self.body = self.data.get("body", None)

    async def api_call(self):
        async with aiohttp.ClientSession() as session:
            if self.method == "GET":
                async with session.get(self.url) as response:
                    data = await response.text()
                    logger.info(data)

            elif self.method == "POST":
                async with session.post(self.url, data=self.body) as response:
                    data = await response.text()
                    logger.info(data)

            else:
                logger.info("Invalid method")

    async def start(self):
        await self.api_call()
        logger.info(f"{self.name} task completed")


# Start the event loop and make the API call
# loop = asyncio.get_event_loop()
# task = loop.create_task(SequenceApiCall('api_call_name', data='url_and_method_here').start())
# loop.run_until_complete(task)


class SequenceMilkRun(ServiceSequence):
    """
    For milk run robotic task
    """

    def __init__(self, name: str, serviceId: str, data=None, userGroup=None):
        super().__init__(name, serviceId)
        self.data = data
        self.start_location = self.data["start"]
        # self.start_location = "comfort_2"
        self.location = None

        # step 0 - initialize an empty delivered zone list
        self.delivered_zones = set()
        # demo_env = app_config.demo_env
        self.pudu_robot = app_config.environments["pudu_robot"]
        self.pudu_fleet = app_config.environments["pudu_fleet"]
        self.pudu_charger = app_config.environments["pudu_start"]
        self.delay = app_config.delays["milk_run"]
        self.pudu_moved = False

    async def start(self):

        # while True:
        # configurable params
        for _ in range(6):
            # get occupied comfort zone list
            occupied_zones = self.sm.get_comfort_slots()

            # undelivered = occupied - delivered
            undelivered_zones = sorted(set(occupied_zones) - self.delivered_zones)
            logger.info(f"undelivered zones before moving off {undelivered_zones}")

            # if data.start is NOT empty, send pudu to dat zone first.
            if self.start_location:
                self.pudu_moved = True
                self.location = self.start_location
                self.delivered_zones.add(self.location)
                self.start_location = None
                logger.info(f"SENDING PUDU TO SPECIFIED {self.location}")
                await self.send_robot(self.location)
            # if still have undelivered, send pudu to undelivered zone
            elif undelivered_zones:
                self.pudu_moved = True
                self.location = undelivered_zones.pop(0)
                self.delivered_zones.add(self.location)
                logger.info(f"SENDING PUDU TO SORTED {self.location}")
                await self.send_robot(self.location)
                logger.info(f"undelivered zones after moving off {undelivered_zones}")
            # return pudu if all delivered
            elif self.pudu_moved and not undelivered_zones:
                logger.info(f"RETURNING PUDU from {self.location}")
                await self.return_robot()
                self.pudu_moved = False

            else:
                logger.info(f"PUDU AT START")

        logger.info(f"MILKRUN SEQUENCE COMPLETED!")

    async def send_robot(self, location):

        pudu_data = {
            "category": "zone",
            "start": location,
            "robot": self.pudu_robot,
            "fleet": self.pudu_fleet,
            "zoneType": "all"
            # "delay": self.delay
        }
        send_robot_task = SequenceRoboticTask(
            name="send_robot", serviceId=self.service_id, data=pudu_data
        )
        await send_robot_task.start()
        play_sound = SequencePuduTask(name="play_sound", delay=self.delay)
        await play_sound.start()

    async def return_robot(self):

        pudu_data = {
            "category": "go_to_place",
            "start": self.pudu_charger,
            "robot": self.pudu_robot,
            "fleet": self.pudu_fleet,
        }

        send_robot_task = SequenceRoboticTask(
            name="send_robot", serviceId=self.service_id, data=pudu_data
        )
        await send_robot_task.start()


class SequenceRoboticTask(ServiceSequence):
    """
    For RMF-related messages.
    (Used for robotics tasks)
    """

    def __init__(self, name: str, serviceId: str, data={}):
        super().__init__(name, serviceId)
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
                # WORKAROUND: to check if AW has completed it go to FF zone task
                if place == "ff":
                    # AW IS IN FF ZONE
                    logger.info(f"AW IN FF ZONE")
                    self.sm.update_aw_in_ff(flag=True)
                logger.info(f"{self.name} task (robotic) completed")
                await self.onComplete()
            elif status in ["failed", "canceled"]:
                await self.onFail()
            else:
                if self.data["robot"] == "piimo_1":
                    self.sm.update_aw_in_ff(flag=False)

    async def onComplete(self):
        logger.info(f"{self.name} task (robotic) completed")
        self.complete_event.set()

    async def onFail(self):
        logger.info(f"{self.name} task (robotic) failed")
        self.complete_event.set()

    async def start(self, start_data=None):
        logger.info(f"{self.name} task (robotic) started")

        robot = self.data["robot"]
        fleet = self.data["fleet"]
        category = self.data["category"]
        place = self.data["start"]
        zoneType = self.data.get("zoneType", None)
        zoneFacing = self.data.get("zoneFacing", None)
        delay = self.data.get("delay", None)
        start = ""

        # if place is a function, call it
        if callable(place):
            start = place()
        else:
            start = place

        # payload = self.rmfTaskBuilder(**self.data)
        payload = rmfTaskBuilder(
            robot=robot,
            fleet=fleet,
            category=category,
            start=start,
            zoneType=zoneType,
            zoneFacing=zoneFacing,
        )

        logger.info(f"RESPONSE: {payload}")

        resp = mdl.TaskDispatchResponse.parse_raw(await tasks_service().call(payload))

        # cancel workflow if request failed
        if not resp.__root__.success:
            raise RobotDispatchFailed(
                robot_id="aw", message=f"Failed to dispatch {robot} to {start}"
            )

        self.task_id = resp.__root__.state.booking.id

        # end this task based on this handler
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

        if delay:
            logger.info(f"Delaying this task for {delay} seconds!!")
            await asyncio.sleep(delay)


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
        self.id = str(uuid.uuid4())
        self.patient_id = None
        self.tasks = []
        self.status = "Idle"
        self.currentTask = None
        self.data = {}
        self.loop = asyncio.get_event_loop()

    def add_sequence(self, sequence: ServiceSequence):
        self.tasks.append(sequence)

    async def start(self):
        self.status = "Running"

        # context_info = {
        #     'patient_id': self.patient_id,
        #     'service_id': self.id,
        #     # .... add other fields
        # }

        for task in self.tasks:
            # inject the service_id into sequenceTasks
            # task.set_context_info(context_info)

            self.currentTask = task

            if isinstance(task, list):  # If task contains multiple sub tasks
                # for sub_task in task:
                #     await sub_task.set_context_info(context_info)
                await asyncio.gather(
                    *(sub_task.start() for sub_task in task)
                )  # Execute all sub tasks concurrently
            else:
                # await task.set_context_info(context_info)
                await task.start()
        self.status = "Completed"
        logger.info(f"Yaaaay! service is completed!!")

    def stop(self):
        if self.currentTask:
            self.currentTask.stop()
        self.status = "Stopped"

    def pause(self):
        if self.currentTask:
            self.currentTask.pause()
        self.status = "Paused"

    def resume(self):
        if self.currentTask:
            self.currentTask.resume()
        self.status = "Running"

    def get_current_seq_name(self):
        return self.currentTask.name if self.currentTask else None


if __name__ == "__main__":
    pass
