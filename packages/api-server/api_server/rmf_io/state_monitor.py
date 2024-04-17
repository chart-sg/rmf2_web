import asyncio
from typing import Callable, Dict, Optional

from reactivex.subject import Subject
from tortoise.contrib.pydantic.base import PydanticModel

from api_server.models import (  # AlertState
    DispenserState,
    DoorState,
    FleetState,
    IngestorState,
    LiftState,
    TaskState,
)

from .events import AlertEvents, FleetEvents, RmfEvents, SensorEvents, TaskEvents


class StateMonitor:
    def __init__(
        self,
        rmf_events: RmfEvents,
        fleet_events: FleetEvents,
        task_events: TaskEvents,
        alert_events: AlertEvents,
        sensor_events: SensorEvents,
        logger,
    ):
        self.rmf = rmf_events
        self.fleet = fleet_events
        self.task = task_events
        self.alert = alert_events
        self.sensor = sensor_events
        self.logger = logger

        # state trackers
        self.states = {
            "door_state": {str: DoorState},
            "dispenser_state": {str: DispenserState},
            "ingestor_state": {str: IngestorState},
            "fleet_state": {str: FleetState},
            "task_state": {str: TaskState},
            "lift_state": {str: LiftState},
            "alert_state": {str: PydanticModel},
            "sensor_state": {str: PydanticModel},
        }

    async def start(self):
        self.rmf.door_states.subscribe(lambda x: self.listener(x, "door_state"))
        self.rmf.dispenser_states.subscribe(
            lambda x: self.listener(x, "dispenser_state")
        )
        self.rmf.ingestor_states.subscribe(lambda x: self.listener(x, "ingestor_state"))
        self.rmf.lift_states.subscribe(lambda x: self.listener(x, "lift_state"))
        self.fleet.fleet_states.subscribe(lambda x: self.listener(x, "fleet_state"))
        self.task.task_states.subscribe(lambda x: self.listener(x, "task_state"))
        self.alert.alerts.subscribe(lambda x: self.listener(x, "alert_state"))
        self.sensor.sensors.subscribe(lambda x: self.listener(x, "sensor_state"))

        # self.task.task_states.subscribe(lambda x: asyncio.create_task(self.task_checker(x)))

        asyncio.create_task(self.periodic_print_states())

    def listener(self, data, attrib_name):
        if attrib_name == "door_state":
            self.states[attrib_name][data.door_name] = data
        elif attrib_name == "dispenser_state" or attrib_name == "ingestor_state":
            self.states[attrib_name][data.guid] = data
        elif attrib_name == "fleet_state":
            self.states[attrib_name][data.name] = data
            # self.logger.warn(f"FLEET: {data}")
        elif attrib_name == "task_state":
            # self.logger.warn(f"TASK: {data}")
            self.states[attrib_name][data.booking.id] = data
        elif attrib_name == "lift_state":
            self.states[attrib_name][data.lift_name] = data
        elif attrib_name == "alert_state":
            self.logger.warn(f"ALERT: {data}")
            # self.states[attrib_name][data.alert_id] = data
        elif attrib_name == "sensor_state":
            self.logger.warn(f"sensor event: {data}")
        else:
            self.states[attrib_name] = data

    def get_task(self, id: str):

        if id in self.states["task_state"]:
            return self.states["task_state"][id]
        return None

    def get_task_action_status(
        self, task_data: TaskState, action: str, place: str = ""
    ):

        for phase in task_data.phases.values():
            for event in phase.events.values():
                if place:
                    if event.name == f"{action} [place:{place}]":
                        return event.status.value
                else:
                    if event.name == action:
                        return event.status.value
        return None

    def get_ack_status(self, alert_data: PydanticModel):

        self.logger.warn(f"ALERT ACKAAAA: {alert_data.acknowledged_by}")
        if alert_data.acknowledged_by:
            return True
        else:
            return False

    # if there is a change in the state mode that we depend on, then we should trigger a check

    def pos_checker(self, pos1, pos2, threshold=1.0):
        distance = ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
        return distance <= threshold

    def get_robot_position(self, robot: str, fleet: str):
        self.logger.warn(
            f"ASRAF {self.states['fleet_state'][fleet].robots[robot].location}"
        )
        x = self.states["fleet_state"][fleet].robots[robot].location.x
        y = self.states["fleet_state"][fleet].robots[robot].location.y
        # self.logger.warn(f"x: {x}")
        # self.logger.warn(f"y: {y}")

        return [x, y]

    async def periodic_print_states(self):
        while True:
            for attrib_name, state_dict in self.states.items():
                # self.logger.warn(f"{attrib_name}: {state_dict}")
                pass
            await asyncio.sleep(2)


_state_monitor: Optional[StateMonitor] = None


def stateMonitor(
    rmf_events: RmfEvents = None,
    fleet_events: FleetEvents = None,
    task_events: TaskEvents = None,
    alert_events: AlertEvents = None,
    sensor_events: SensorEvents = None,
    logger=None,
):
    global _state_monitor
    if _state_monitor is None:
        _state_monitor = StateMonitor(
            rmf_events, fleet_events, task_events, alert_events, sensor_events, logger
        )
    return _state_monitor
