# pragma: no cover

import asyncio
import base64
import hashlib
import logging
import uuid
from time import sleep
from typing import Any, List, Optional

import rclpy
import rclpy.client
import rclpy.qos
from action_msgs.msg import GoalStatus
from builtin_interfaces.msg import Time as RosTime
from fastapi import HTTPException
from rclpy.action import ActionClient
from rclpy.subscription import Subscription
from rmf_building_map_msgs.msg import AffineImage as RmfAffineImage
from rmf_building_map_msgs.msg import BuildingMap as RmfBuildingMap
from rmf_building_map_msgs.msg import Level as RmfLevel
from rmf_dispenser_msgs.msg import DispenserState as RmfDispenserState
from rmf_door_msgs.msg import DoorMode as RmfDoorMode
from rmf_door_msgs.msg import DoorRequest as RmfDoorRequest
from rmf_door_msgs.msg import DoorState as RmfDoorState

# from rmf_fleet_msgs.msg import BeaconState, ModeRequest, RobotMode
from rmf_fleet_msgs.msg import ModeRequest, RobotMode
from rmf_ingestor_msgs.msg import IngestorState as RmfIngestorState
from rmf_lift_msgs.msg import LiftRequest as RmfLiftRequest
from rmf_lift_msgs.msg import LiftState as RmfLiftState
from rmf_sensor_actions.action import ObjectQuery
from rmf_task_msgs.srv import CancelTask as RmfCancelTask
from rmf_task_msgs.srv import SubmitTask as RmfSubmitTask
from rosidl_runtime_py.convert import message_to_ordereddict

from api_server.app_config import app_config
from api_server.rmf_io.state_monitor import stateMonitor

from .logger import logger as base_logger
from .models import (
    BuildingMap,
    DispenserState,
    DoorState,
    IngestorState,
    LiftState,
    ObjectZone,
)
from .repositories import CachedFilesRepository, cached_files_repo
from .rmf_io import rmf_events, sensor_events
from .ros import ros_node

# from .ros_pydantic import rmf2_sensor_msgs
# from action_tutorials_interfaces.action import Fibonacci


def process_building_map(
    rmf_building_map: RmfBuildingMap,
    cached_files: CachedFilesRepository,
) -> BuildingMap:
    """
    1. Converts a `BuildingMap` message to an ordered dict.
    2. Saves the images into `{cache_directory}/{map_name}/`.
    3. Change the `AffineImage` `data` field to the url of the image.
    """
    processed_map = message_to_ordereddict(rmf_building_map)

    for i, level in enumerate(rmf_building_map.levels):
        level: RmfLevel
        for j, image in enumerate(level.images):
            image: RmfAffineImage
            # look at non-crypto hashes if we need more performance
            sha1_hash = hashlib.sha1()
            sha1_hash.update(image.data)
            fingerprint = base64.b32encode(sha1_hash.digest()).lower().decode()
            relpath = f"{rmf_building_map.name}/{level.name}-{image.name}.{fingerprint}.{image.encoding}"  # pylint: disable=line-too-long
            urlpath = cached_files.add_file(image.data, relpath)
            processed_map["levels"][i]["images"][j]["data"] = urlpath
    return BuildingMap(**processed_map)


class RmfGateway:
    def __init__(
        self,
        cached_files: CachedFilesRepository,
        *,
        logger: Optional[logging.Logger] = None,
    ):
        self._door_req = ros_node().create_publisher(
            RmfDoorRequest, "adapter_door_requests", 10
        )
        self._lift_req = ros_node().create_publisher(
            RmfLiftRequest, "adapter_lift_requests", 10
        )
        self._mode_req = ros_node().create_publisher(
            ModeRequest, "action_execution_notice", 1
        )

        self._submit_task_srv = ros_node().create_client(RmfSubmitTask, "submit_task")
        self._cancel_task_srv = ros_node().create_client(RmfCancelTask, "cancel_task")

        # obj query action client
        self._obj_query_client = ActionClient(
            ros_node(), ObjectQuery, "request_object_query"
        )

        self.cached_files = cached_files
        self.logger = logger or base_logger.getChild(self.__class__.__name__)
        self._subscriptions: List[Subscription] = []
        self.msg_hash_set = set()
        self.comfort_list = set()
        self.goal_loop_flag = True
        self.bed_exit_goal_handle = None
        self.bed_exit_goal = None
        self.enable_bed_exit = True
        self.current_bed_exit_id = None
        # self.comfort_trigger = False
        # self.trigger_time = None

        self._subscribe_all()

    def obj_feedback_callback(self, feedback_msg, goal_id=None):

        # WORKAROUND: only trigger bed exit for current goal handle
        if goal_id:
            if goal_id != self.current_bed_exit_id:
                self.logger.info("Ignoring feedback for previous goal")
                return

        feedback_hash = hashlib.sha256(str(feedback_msg).encode()).hexdigest()
        # check if we received this feedback_msg before
        if feedback_hash in self.msg_hash_set:
            self.logger.info("Duplicated obj detected and skipped")
            return
        # add the hash of feedback_msg to set
        self.msg_hash_set.add(feedback_hash)

        feedback = feedback_msg.feedback
        object_dict = message_to_ordereddict(feedback.object)
        objectZone = ObjectZone(zones=feedback.zones, **object_dict)
        # self.logger.info(f'classification!!!: {objectZone.classification}')

        if objectZone.classification == "wheelchair":
            # self.logger.info(f'object received!!!: {objectZone}')
            comforts = [zone for zone in feedback.zones if zone.startswith("comfort_")]
            self.comfort_list.update(comforts)
            # sensor_events.sensors.on_next(objectZone)

        else:
            sensor_events.sensors.on_next(objectZone)

    async def set_goal_loop(self, mode):
        self.goal_loop_flag = mode
        if mode:
            asyncio.create_task(self.goal_loop())

    async def goal_loop(self):
        while self.goal_loop_flag:
            result = await self.send_goal("zone")
            await asyncio.sleep(5)
        stateMonitor().update_comfort_slots(set())

    # ISSUE: unable to cancel bed exit goal handle
    async def set_bed_exit(self, mode):

        # clear bed_exit task and handle
        if self.bed_exit_goal is not None:
            self.logger.info(f"cancelling existing BED EXIT goal")
            self.bed_exit_goal.cancel()
            self.bed_exit_goal = None

        if self.bed_exit_goal_handle is not None:
            self.logger.info(f"cancelling existing BED EXIT goal handle")
            cancel_result = await self.bed_exit_goal_handle.cancel_goal_async()
            self.logger.info(f"cancel result: {cancel_result}")

            # Check the status of the goal after cancellation
            status = self.bed_exit_goal_handle.status
            self.logger.info(f"Goal status after cancellation: {status}")

            if status == GoalStatus.STATUS_CANCELED:
                self.logger.info("Goal successfully canceled")
            else:
                self.logger.warning(f"Goal not canceled, current status: {status}")

            self.bed_exit_goal_handle = None

        self.enable_bed_exit = mode

        if mode:
            # self.enable_bed_exit = True
            self.logger.info(f"ENABLING BED EXIT")

            # create bed exit task
            self.bed_exit_goal = asyncio.create_task(self.send_goal("bed_exit"))

        else:
            # self.enable_bed_exit = False
            self.logger.info(f"STOPPED BED EXIT")

    async def send_goal(self, goal_type: str):
        self.logger.info(f"ObjectQuery: sending {goal_type} goal")
        goal_msg = ObjectQuery.Goal()

        if goal_type == "bed_exit":
            goal_msg.type = 2
            goal_msg.type_vector = ["bed_exit"]
            goal_msg.run_type = 0
            goal_msg.run_value = 0
        elif goal_type == "zone":
            # need to clear the comfort_array
            self.comfort_list.clear()

            goal_msg.type = 2
            goal_msg.type_vector = ["wheelchair"]
            goal_msg.run_type = 0
            goal_msg.run_value = 1
        else:
            raise Exception(f"Invalid goal {goal_type}")

        # try:
        self._obj_query_client.wait_for_server()

        # WORKAROUND: unique goal id to workaround goal handle cant cancel issue
        if goal_type == "bed_exit":
            # Generate a unique identifier for the new goal
            self.current_bed_exit_id = uuid.uuid4()
            goal_id = self.current_bed_exit_id
        else:
            goal_id = None

        # goal_handle = await self._obj_query_client.send_goal_async(
        #     goal=goal_msg, feedback_callback=self.obj_feedback_callback
        # )

        goal_handle = await self._obj_query_client.send_goal_async(
            goal=goal_msg,
            feedback_callback=lambda feedback: self.obj_feedback_callback(
                feedback, goal_id
            ),
        )
        await asyncio.sleep(1)

        if goal_type == "bed_exit":
            self.bed_exit_goal_handle = goal_handle

        if goal_type == "zone":
            result = await goal_handle.get_result_async()

        stateMonitor().update_comfort_slots(self.comfort_list)

        return self.comfort_list

    # async def send_goal_obj(self, client: rclpy.action.ActionClient, goal, timeout=1) -> Any:
    async def send_goal_obj(self, goal, fb, timeout=1) -> Any:
        """
        Utility to wrap a ros action goal in an awaitable,
        raises Exception if the goal process fails.
        """
        # fut = client.send_goal_async(goal=goal, feedback_callback=self.obj_feedback_callback)
        fut = self._obj_query_client.send_goal_async(goal=goal, feedback_callback=fb)
        try:
            res = await asyncio.wait_for(fut, timeout=timeout)
            return res
        except asyncio.TimeoutError as e:
            raise Exception("ROS action goal processing timed out") from e

    async def call_service(self, client: rclpy.client.Client, req, timeout=1) -> Any:
        """
        Utility to wrap a ros service call in an awaitable,
        raises HTTPException if service call fails.
        """
        fut = client.call_async(req)
        try:
            result = await asyncio.wait_for(fut, timeout=timeout)
            return result
        except asyncio.TimeoutError as e:
            raise HTTPException(503, "ros service call timed out") from e

    def _subscribe_all(self):
        door_states_sub = ros_node().create_subscription(
            RmfDoorState,
            "door_states",
            lambda msg: rmf_events.door_states.on_next(DoorState.from_orm(msg)),
            10,
        )
        self._subscriptions.append(door_states_sub)

        def convert_lift_state(lift_state: RmfLiftState):
            dic = message_to_ordereddict(lift_state)
            return LiftState(**dic)

        lift_states_sub = ros_node().create_subscription(
            RmfLiftState,
            "lift_states",
            lambda msg: rmf_events.lift_states.on_next(convert_lift_state(msg)),
            10,
        )
        self._subscriptions.append(lift_states_sub)

        dispenser_states_sub = ros_node().create_subscription(
            RmfDispenserState,
            "dispenser_states",
            lambda msg: rmf_events.dispenser_states.on_next(
                DispenserState.from_orm(msg)
            ),
            10,
        )
        self._subscriptions.append(dispenser_states_sub)

        ingestor_states_sub = ros_node().create_subscription(
            RmfIngestorState,
            "ingestor_states",
            lambda msg: rmf_events.ingestor_states.on_next(IngestorState.from_orm(msg)),
            10,
        )
        self._subscriptions.append(ingestor_states_sub)

        map_sub = ros_node().create_subscription(
            RmfBuildingMap,
            "map",
            lambda msg: rmf_events.building_map.on_next(
                process_building_map(msg, self.cached_files)
            ),
            rclpy.qos.QoSProfile(
                history=rclpy.qos.HistoryPolicy.KEEP_ALL,
                depth=1,
                reliability=rclpy.qos.ReliabilityPolicy.RELIABLE,
                durability=rclpy.qos.DurabilityPolicy.TRANSIENT_LOCAL,
            ),
        )
        self._subscriptions.append(map_sub)

        # def convert_sensor_state(beacon_state: BeaconState):
        #     dic = message_to_ordereddict(beacon_state)
        #     return BeaconState(**dic)

        # sensor_sub = ros_node().create_subscription(
        #     BeaconState,
        #     "sensor_state",
        #     lambda msg: sensor_events.sensors.on_next(convert_sensor_state(msg)),
        #     10,
        # )
        # self._subscriptions.append(sensor_sub)

    @staticmethod
    def now() -> Optional[RosTime]:
        """
        Returns the current sim time, or `None` if not using sim time
        """
        return ros_node().get_clock().now().to_msg()

    def request_door(self, door_name: str, mode: int) -> None:
        msg = RmfDoorRequest(
            door_name=door_name,
            request_time=ros_node().get_clock().now().to_msg(),
            requester_id=ros_node().get_name(),  # FIXME: use username
            requested_mode=RmfDoorMode(
                value=mode,
            ),
        )
        self._door_req.publish(msg)

    def request_lift(
        self, lift_name: str, destination: str, request_type: int, door_mode: int
    ):
        msg = RmfLiftRequest(
            lift_name=lift_name,
            request_time=ros_node().get_clock().now().to_msg(),
            session_id=ros_node().get_name(),
            request_type=request_type,
            destination_floor=destination,
            door_state=door_mode,
        )
        self._lift_req.publish(msg)

    def request_mode(
        self, fleet_name: str, robot_name: str, mode: int, task_id: str = ""
    ):
        msg = ModeRequest(
            fleet_name=fleet_name,
            robot_name=robot_name,
            mode=RobotMode(mode=mode),
            task_id=task_id,
        )
        self._mode_req.publish(msg)


# _rmf_gateway: RmfGateway
_rmf_gateway: Optional[RmfGateway] = None


def rmf_gateway() -> RmfGateway:
    return _rmf_gateway


def startup():
    """
    Starts subscribing to all ROS topics.
    Must be called after the ros node is created and before spinning the it.
    """
    global _rmf_gateway
    _rmf_gateway = RmfGateway(cached_files_repo)

    # _rmf_gateway.send_goal()
    return _rmf_gateway
