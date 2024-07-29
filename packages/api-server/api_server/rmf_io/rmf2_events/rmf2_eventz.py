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


class Events:
    """
    A event item, contains the
    event listener and event handler

    """

    def __init__(self, name: str, stream: SensorEvents, loop, service=None):
        self.name = name
        self.stream = stream
        self.loop = loop
        self.service = service
        self.subscription = None
        self.task = None

    async def start(self):
        logger.info(f"starting {self.name} listener")
        self.task = self.loop.create_task(self.listener())

    async def stop(self):
        logger.info(f"stopping {self.name} listener")
        if self.subscription:
            self.subscription.dispose()
            self.subscription = None
        if self.task:
            self.task.cancel()

    async def listener(self):
        self.subscription = self.stream.sensors.subscribe(
            lambda x: self.loop.create_task(self.handler(data=x))
        )

    async def handler(self, data="test"):
        logger.info(f"handling {self.name} data!")
        await asyncio.sleep(10)
        logger.info(f"handling {self.name} complete!")


class BedExitEvent(Events):
    """
    A specific event for bed exit that overrides the handler
    """

    async def handler(self, data="test"):

        if data.classification == "bed_exit":
            logger.warn(f"bed_exit event triggered")


class EventManager:

    """
    An Manager class containing the event items,
    runs all event items on startup,
    that will listen to condition,
    which triggers their respective services
    """

    def __init__(self, sensor_events, logger):
        self.event_objects = []
        self.sensor = sensor_events
        self.logger = logger
        self.rmf_gateway = rmf_gateway()
        self._loop = asyncio.get_event_loop()
        self.bed_exit = BedExitEvent(
            name="bed_exit", stream=sensor_events, loop=self._loop
        )

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
            self._loop.create_task(self.rmf_gateway.send_goal("bed_exit"))
            self.event_objects.append(self.bed_exit)

        await asyncio.gather(*(event.start() for event in self.event_objects))


_event_manager: Optional[EventManager] = None


def eventManagerz(sensor_events: SensorEvents = None, logger=None):
    global _event_manager
    if _event_manager is None:
        _event_manager = EventManager(sensor_events, logger)
    return _event_manager
