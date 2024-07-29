import asyncio
import concurrent.futures
import json
import logging
from collections import namedtuple
from typing import Coroutine, List, Optional

from reactivex.abc import DisposableBase
from reactivex.subject import Subject

from api_server.app_config import app_config
from api_server.gateway import rmf_gateway
from api_server.logger import logger

from ..events import SensorEvents

# from api_server.rmf_io.state_monitor import stateMonitor
# from api_server.workflows import BedExitFlow, MilkRunFlow
# from .bed_exit_event import bedExitEvent


# class Data:
#     def __init__(self):
#         self.robot_id = "temi"


# class Service:
#     def __init__(self):
#         self.service_id = "test"
#         self.data = Data()


class EventHandler:
    """
    A handler class that checks the data with a condition,
    which triggers the service if the condition is met.
    """

    def __init__(self, service, handler_function):
        self.service = service
        self.handler_function = handler_function

    async def handle_event(self, data):
        try:
            logger.warn("I LIKE BOOTY")
            await self.handler_function(data, self.service)
        except Exception as e:
            logger.error(f"Error handling event: {e}")


class EventListener:
    """
    A listener class that listens to streams of data
    and updates them to the event object it belongs to.
    """

    def __init__(self, stream, handler: EventHandler):
        self.name = "bed_exit"
        self.stream = stream
        self.handler = handler
        self.subscription = None
        self._loop = asyncio.get_event_loop()

    async def start(self):
        self.subscription = self.stream.subscribe(lambda x: self._on_event_received(x))
        # self.subscription = self.stream.subscribe(
        #         lambda x: self._create_listener(
        #             self.handler.handle_event(data=x)
        #         )
        # )
        logger.info(f"{self.name} subscription started")

    async def hello(self, data="Asraf"):
        logger.warn(f"SOMEBODY SAVE ME! {data}")
        await asyncio.sleep(1)
        logger.warn(f"Hello function completed")

    def _on_event_received(self, data):
        logger.info(f"Event received: {data}")
        # self.hello()
        self._create_listener(self.hello())

    async def stop(self):
        if self.subscription:
            self.subscription.dispose()
            self.subscription = None
            logger.info(f"{self.name} subscription disposed")

    def _create_listener(self, coro: Coroutine):
        # return self._loop.create_task(coro)
        logger.info(f"Creating listener for coroutine: {coro}")
        task = self._loop.create_task(coro)
        task.add_done_callback(self._task_done_callback)
        logger.info(f"Task created: {task}")
        return task

    def _task_done_callback(self, task):
        try:
            result = task.result()
            logger.info(f"Task completed with result: {result}")
        except Exception as e:
            logger.error(f"Task raised an exception: {e}")


class Events:
    """
    A event item, contains the
    event listener and event handler

    """

    def __init__(
        self,
        name: str,
        service,
        stream,
        gateway,
        handler: EventHandler = None,
        listener: EventListener = None,
    ):
        self.name = name
        self.service = service
        self.stream = stream
        # self.loop = asyncio.get_event_loop()

        # gateway to rmf and objectquery
        self.rmf_gateway = gateway

        # listener and handler
        self.handler = handler
        self.listener = listener

        self.task = None
        self.subscription = None

    async def start(self):
        logger.warn(f"starting {self.name} listener")
        await self.listener.start()

    async def stop(self):
        logger.warn(f"stopping {self.name} listener")
        await self.listener.stop()


class EventManager:
    """
    An Manager class containing the event items,
    runs all event items on startup,
    that will listen to condition,
    which triggers their respective services
    """

    def __init__(self, sensor_events: SensorEvents, logger):
        self.event_objects = []
        self.sensor = sensor_events
        self.logger = logger
        self.rmf_gateway = rmf_gateway()
        self._loop = asyncio.get_event_loop()

    def _create_task(self, coro: Coroutine):
        task = self._loop.create_task(coro)

    async def stop_event(self, event_name: str):
        for event in self.event_objects:
            if event.name == event_name:
                await event.stop()
                self.event_objects.remove(event)
                logger.info(f"Stopped and removed event: {event_name}")
                return
        logger.warning(f"Event {event_name} not found")

    async def add_event(self, event):
        self.event_objects.append(event)
        # self._create_task(event.start())
        logger.info(f"Added and started event: {event.name}")

    async def start(self):

        if app_config.event["test"]:
            logger.info(f"send bed_exit goal")
            asyncio.create_task(self.rmf_gateway.send_goal("bed_exit"))

        await asyncio.gather(*(event.start() for event in self.event_objects))


_event_manager: Optional[EventManager] = None


def eventManagerDev(sensor_events: SensorEvents = None, logger=None):
    global _event_manager
    if _event_manager is None:
        _event_manager = EventManager(sensor_events, logger)
    return _event_manager
