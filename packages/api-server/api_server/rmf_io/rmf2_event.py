import asyncio
import json
import logging
from collections import namedtuple
from typing import Coroutine, List, Optional

from reactivex.abc import DisposableBase
from reactivex.subject import Subject

from api_server.logger import logger
from api_server.workflows import TestFlow

from .events import SensorEvents


class Data:
    def __init__(self):
        self.robot_id = "aw"


class Service:
    def __init__(self):
        self.service_id = "test"
        self.data = Data()


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

    def _create_task(self, coro: Coroutine):
        task = self._loop.create_task(coro)

    async def start(self):
        self._loop = asyncio.get_event_loop()

        # declare all event items
        # service_data = {"service_id": "test", "data": {"robot_id":"aw"}}

        service_data = Service()
        bed_exit = Events(
            name="bed_exit",
            service=TestFlow(service_data),
            stream=self.sensor.sensors,
            loop=self._loop,
        )
        self.event_objects.append(bed_exit)

        await asyncio.gather(*(event.start() for event in self.event_objects))


class Events:
    """
    A event item, contains the
    the trigger condition,
    service to run,

    """

    def __init__(self, name: str, service, stream, loop):
        self.name = name
        self.service = service
        self.stream = stream
        self.loop = loop

    async def condition_handler(self, data):
        if data.category == "bed_exit":
            logger.warn(f"bed exit TRIGGERED")
            await self.service.start_workflow()

    async def start(self):
        logger.warn(f"starting bed exit listener")

        self.stream.subscribe(
            lambda x: self._create_listener(self.condition_handler(x))
        )

    def _create_listener(self, coro: Coroutine):
        task = self.loop.create_task(coro)


_event_manager: Optional[EventManager] = None


def eventManager(sensor_events: SensorEvents = None, logger=None):
    global _event_manager
    if _event_manager is None:
        _event_manager = EventManager(sensor_events, logger)
    return _event_manager
