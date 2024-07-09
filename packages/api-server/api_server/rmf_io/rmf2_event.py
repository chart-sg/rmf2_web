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
from api_server.rmf_io.state_monitor import stateMonitor
from api_server.workflows import BedExitFlow, MilkRunFlow

from .events import SensorEvents


class Data:
    def __init__(self):
        self.robot_id = "temi"


class Service:
    def __init__(self):
        self.service_id = "test"
        self.data = Data()


async def bed_exit_handler(data, service):
    if data.classification == "bed_exit":
        logger.warn(f"bed_exit event triggered")

        logger.warn(f"BED EXIT ENABLED?: {rmf_gateway().enable_bed_exit}")
        if rmf_gateway().enable_bed_exit == False:
            return

        if "/" in data.direction:
            direction, video = data.direction.split("/", maxsplit=1)
        else:
            direction = data.direction
            video = ""

        logger.warn(f"ZONE: {data.zones[0]} , direction: {direction}")
        # logger.warn(f"VIDEO: {video}")

        # inverse_direction = "right" if data.direction == "left" else "left"
        await service.start_workflow(
            data={"zone": data.zones[0], "direction": direction}
        )


# async def milk_run_handler(data, service):
#         if data.classification == "wheelchair":
#             logger.warn(f"milk_run event triggered")
#             comforts = [zone for zone in data.zones if zone.startswith('comfort_')]
#             logger.warn(f"ZONE: {comforts}")

# await service.start_workflow(data={'zone': data.zones[0],'direction':data.direction})


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

    def _create_task(self, coro: Coroutine):
        task = self._loop.create_task(coro)

    async def stop(self, event: str):
        pass

    async def start(self):
        self._loop = asyncio.get_event_loop()

        # declare all event items
        # service_data = {"service_id": "test", "data": {"robot_id":"aw"}}

        service_data = Service()
        # rmf_gateway().send_goal("zone")

        bed_exit = Events(
            name="bed_exit",
            service=BedExitFlow(service_data),
            handler=bed_exit_handler,
            stream=self.sensor.sensors,
            gateway=self.rmf_gateway,
        )
        # bed_exit = BedExitEvent(
        #     service=BedExitFlow(service_data),
        #     stream=self.sensor.sensors,
        #     gateway=self.rmf_gateway
        # )

        milk_run = Events(
            name="milk_run",
            service=MilkRunFlow(),
            stream=self.sensor.sensors,
            gateway=self.rmf_gateway,
        )

        if app_config.event["bed_exit"]:
            # asyncio.create_task(self.rmf_gateway.set_bed_exit(True))
            asyncio.create_task(self.rmf_gateway.send_goal("bed_exit"))
            self.event_objects.append(bed_exit)

        if app_config.event["milk_run"]:
            asyncio.create_task(self.rmf_gateway.goal_loop())
            self.event_objects.append(milk_run)

        # self.event_objects.append(bed_exit)
        # self.event_objects.append(milk_run)

        await asyncio.gather(*(event.start() for event in self.event_objects))


class Events:
    """
    A event item, contains the
    the trigger condition,
    service to run,

    """

    def __init__(self, name: str, service, stream, gateway, handler=None):
        self.name = name
        self.service = service
        self.handler = handler
        self.stream = stream
        self.loop = asyncio.get_event_loop()
        self.comfort_set = set()
        self.rmf_gateway = gateway
        self.state_monitor = stateMonitor()
        self.double_confirm = False

    # async def condition_handler(self, data):
    #     if data.classification == "bed_exit":
    #         logger.warn(f"{self.name} event triggered")
    #         logger.warn(f"ZONE: {data.zones[0]} , direction {data.direction}")
    #         await self.service.start_workflow(data={'zone': data.zones[0],'direction':data.direction})

    async def milk_run(self):
        while True:

            result = self.state_monitor.get_comfort_slots()
            result = set(result)
            # logger.warn(f"ASRAF GET comfort slots: {result}")

            # logger.warn(f"saved state: {self.comfort_set}")
            # logger.warn(f"result state: {result}")

            if self.comfort_set != result:  # theres a difference
                logger.warn(f"theres a state change! {result}")

                if not self.double_confirm:
                    self.double_confirm = True
                    logger.warn(f"set double confirm to True!")
                    await asyncio.sleep(5)
                    continue

                self.double_confirm = False
                final_set = result - self.comfort_set
                logger.warn(f"FINAL SET: {final_set}")
                self.comfort_set = result

                if final_set:  # if someone new came in
                    logger.warn(f"{final_set} IS NEWLY OCCUPIED!")
                    sorted_list = sorted(list(final_set))

                    await self.service.start_workflow({"start": sorted_list[0]})

                    # set result to latest
                    result = self.state_monitor.get_comfort_slots()
                    result = set(result)
                    self.comfort_set = result
                else:
                    pass
                    # logger.warn(f"SOMEONE LEFT!")
            else:
                if self.double_confirm:
                    logger.warn(f"RESETTING DOUBLE CONFIRM")
                    self.double_confirm = False

            await asyncio.sleep(5)

    async def start(self):
        logger.warn(f"starting {self.name} listener")

        if self.name == "milk_run":
            task = self._create_listener(self.milk_run())
        else:
            self.stream.subscribe(
                lambda x: self._create_listener(
                    self.handler(data=x, service=self.service)
                )
            )

    def _create_listener(self, coro: Coroutine):
        task = self.loop.create_task(coro)


# FUTURE DEVELOPMENT
# class BedExitEvent(Events):
#     def __init__(self, service, stream, gateway):
#         self.name = "bed_exit"
#         self.service = service
#         self.stream = stream
#         self.loop = asyncio.get_event_loop()
#         self.comfort_set = set()
#         self.rmf_gateway = gateway

#     async def handler(data, service):
#         logger.warn(f"BED EXIT: {data}")
#         # if data.classification=="bed_exit":
#         if "bed_exit" in data.classification:
#             logger.warn(f"bed_exit event triggered")
#             logger.warn(f"ZONE: {data.zones[0]} , direction {data.direction}")

#             inverse_direction = "right" if data.direction == "left" else "left"

#             await service.start_workflow(
#                 data={"zone": data.zones[0], "direction": inverse_direction}
#             )

#     async def start(self):
#         logger.warn(f"starting {self.name} listener")
#         self.stream.subscribe(
#             lambda x: self._create_listener(self.handler(data=x, service=self.service))
#         )


_event_manager: Optional[EventManager] = None


def eventManager(sensor_events: SensorEvents = None, logger=None):
    global _event_manager
    if _event_manager is None:
        _event_manager = EventManager(sensor_events, logger)
    return _event_manager
