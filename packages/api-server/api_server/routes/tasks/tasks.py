import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple, cast

from fastapi import Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel
from reactivex import operators as rxops

from api_server import models as mdl
from api_server.dependencies import (
    between_query,
    finish_time_between_query,
    pagination_query,
    sio_user,
    start_time_between_query,
)
from api_server.fast_io import FastIORouter, SubscriptionRequest
from api_server.gateway import rmf_gateway
from api_server.logger import logger
from api_server.models.tortoise_models import TaskState as DbTaskState
from api_server.mqtt_client import mqtt_client
from api_server.repositories import TaskRepository, task_repo_dep
from api_server.response import RawJSONResponse
from api_server.rmf_io import task_events, tasks_service
from api_server.workflows import (
    AdhocDeliveryFlow,
    AdmitWardFlow,
    AwPatientExitFlow,
    BedAvailFlow,
    BedExitFlow,
    MilkRunFlow,
    PatientOrientationFlow,
    ReturnRobotFlow,
    SendAWFlow,
    SendFFFlow,
    TemiManualFlow,
    TestFlow,
    ViewPatientFlow,
)

router = FastIORouter(tags=["Tasks"])


@router.get("/{task_id}/request", response_model=mdl.TaskRequest)
async def get_task_request(
    task_repo: TaskRepository = Depends(task_repo_dep),
    task_id: str = Path(..., description="task_id"),
):
    result = await task_repo.get_task_request(task_id)
    if result is None:
        raise HTTPException(status_code=404)
    return result


@router.get("", response_model=List[mdl.TaskState])
async def query_task_states(
    task_repo: TaskRepository = Depends(task_repo_dep),
    task_id: Optional[str] = Query(
        None, description="comma separated list of task ids"
    ),
    category: Optional[str] = Query(
        None, description="comma separated list of task categories"
    ),
    assigned_to: Optional[str] = Query(
        None, description="comma separated list of assigned robot names"
    ),
    start_time_between: Optional[Tuple[datetime, datetime]] = Depends(
        start_time_between_query
    ),
    finish_time_between: Optional[Tuple[datetime, datetime]] = Depends(
        finish_time_between_query
    ),
    status: Optional[str] = Query(None, description="comma separated list of statuses"),
    pagination: mdl.Pagination = Depends(pagination_query),
):
    filters = {}
    if task_id is not None:
        filters["id___in"] = task_id.split(",")
    if category is not None:
        filters["category__in"] = category.split(",")
    if assigned_to is not None:
        filters["assigned_to__in"] = assigned_to.split(",")
    if start_time_between is not None:
        filters["unix_millis_start_time__gte"] = start_time_between[0]
        filters["unix_millis_start_time__lte"] = start_time_between[1]
    if finish_time_between is not None:
        filters["unix_millis_finish_time__gte"] = finish_time_between[0]
        filters["unix_millis_finish_time__lte"] = finish_time_between[1]
    if status is not None:
        valid_values = [member.value for member in mdl.Status]
        filters["status__in"] = []
        for status_string in status.split(","):
            if status_string not in valid_values:
                continue
            filters["status__in"].append(mdl.Status(status_string))

    return await task_repo.query_task_states(DbTaskState.filter(**filters), pagination)


@router.get("/{task_id}/state", response_model=mdl.TaskState)
async def get_task_state(
    task_repo: TaskRepository = Depends(task_repo_dep),
    task_id: str = Path(..., description="task_id"),
):
    """
    Available in socket.io
    """
    result = await task_repo.get_task_state(task_id)
    if result is None:
        raise HTTPException(status_code=404)
    return result


@router.sub("/{task_id}/state", response_model=mdl.TaskState)
async def sub_task_state(req: SubscriptionRequest, task_id: str):
    user = sio_user(req)
    task_repo = TaskRepository(user)
    obs = task_events.task_states.pipe(rxops.filter(lambda x: x.booking.id == task_id))
    current_state = await get_task_state(task_repo, task_id)
    if current_state:
        return obs.pipe(rxops.start_with(current_state))
    return obs


@router.get("/{task_id}/log", response_model=mdl.TaskEventLog)
async def get_task_log(
    task_repo: TaskRepository = Depends(task_repo_dep),
    task_id: str = Path(..., description="task_id"),
    between: Tuple[int, int] = Depends(between_query),
):
    """
    Available in socket.io
    """

    result = await task_repo.get_task_log(task_id, between)
    if result is None:
        raise HTTPException(status_code=404)
    return result


@router.sub("/{task_id}/log", response_model=mdl.TaskEventLog)
async def sub_task_log(_req: SubscriptionRequest, task_id: str):
    return task_events.task_event_logs.pipe(
        rxops.filter(lambda x: x.task_id == task_id)
    )


@router.post("/activity_discovery", response_model=mdl.ActivityDiscovery)
async def post_activity_discovery(
    request: mdl.ActivityDiscoveryRequest = Body(...),
):
    return RawJSONResponse(await tasks_service().call(request.json(exclude_none=True)))


@router.post("/cancel_task", response_model=mdl.TaskCancelResponse)
async def post_cancel_task(
    request: mdl.CancelTaskRequest = Body(...),
):
    return RawJSONResponse(await tasks_service().call(request.json(exclude_none=True)))


class EventType(Enum):
    test = "test"
    bed_exit = "bed_exit"
    milk_run = "milk_run"


class EventRequest(BaseModel):
    event_type: EventType
    mode: bool = True


@router.post("/event_driven")
async def post_service_task(event_request: EventRequest):
    logger.info(f"request event JSON body : {event_request}")
    # for testing
    if event_request.event_type == EventType.test:
        logger.info(f"Event Test triggered")
    # bed exit
    elif event_request.event_type == EventType.bed_exit:
        await rmf_gateway().set_bed_exit(event_request.mode)
    # milk run
    elif event_request.event_type == EventType.milk_run:
        # if event_request.mode == False:
        await rmf_gateway().set_goal_loop(event_request.mode)

    return event_request


# place here for now
class ServiceType(Enum):
    send_aw = "send_aw"
    send_ff = "send_ff"
    admit_ff = "admit_ff"
    admit_ward = "admit_ward"
    adhoc_delivery = "adhoc_delivery"
    return_robot = "return_robot"
    bed_exit = "bed_exit"
    bed_avail = "bed_avail"
    milk_run = "milk_run"
    view_patient = "view_patient"
    aw_patient_exit = "aw_patient_exit"
    patient_orientation = "patient_orientation"
    temi_manual = "temi_manual"
    temi_release = "temi_release"
    test = "test"


class ServiceData(BaseModel):
    robot_id: str = None
    robot_fleet: str = None
    location: str = None
    patient_id: str = None
    zone_type: str = None
    zone_facing: str = None
    patient_id: str = None
    items: str = None


class ServiceTask(BaseModel):
    service_name: ServiceType
    data: ServiceData
    requester: str = None
    requester_group: str = None
    receiver_group: str = None


@router.post("/service_task")
async def post_service_task(service_task: ServiceTask):

    logger.info(f"request JSON body : {service_task}")
    # for testing
    if service_task.service_name == ServiceType.test:
        workflow = TestFlow(service_task)
    # send aw
    elif service_task.service_name == ServiceType.send_aw:
        workflow = SendAWFlow(service_task)
    # admit FF
    elif service_task.service_name == ServiceType.send_ff:
        workflow = SendFFFlow(service_task)
    # admit ward
    elif service_task.service_name == ServiceType.admit_ward:
        workflow = AdmitWardFlow(service_task)
    # adhoc delivery
    elif service_task.service_name == ServiceType.adhoc_delivery:
        workflow = AdhocDeliveryFlow(service_task)
    # return robot
    elif service_task.service_name == ServiceType.return_robot:
        # WORKAROUND: return temi via mqtt
        if service_task.data.robot_id == "bed_responder":
            logger.info(f"PUBLISH TEMI TO CHARGER!")
            mqtt_client().publish(
                f"temi/00119140017/command/waypoint/goto",
                json.dumps({"location": "home base"}),
            )
            return
        # return
        workflow = ReturnRobotFlow(service_task)
    # bed avail
    elif service_task.service_name == ServiceType.bed_avail:
        workflow = BedAvailFlow(service_task)
    # milk run
    elif service_task.service_name == ServiceType.milk_run:
        workflow = MilkRunFlow(service_task)
    # view patient
    elif service_task.service_name == ServiceType.view_patient:
        workflow = ViewPatientFlow(service_task)
    # aw patient exit
    elif service_task.service_name == ServiceType.aw_patient_exit:
        workflow = AwPatientExitFlow(service_task)
        # await rmf_gateway().send_goal("zone")
        # return {"status": "milkrun started"}
    # patient orientation
    elif service_task.service_name == ServiceType.patient_orientation:
        workflow = PatientOrientationFlow(service_task)
    # temi manual control
    elif service_task.service_name == ServiceType.temi_manual:
        workflow = TemiManualFlow(service_task)
    # temi release
    elif service_task.service_name == ServiceType.temi_release:
        logger.info(f"ENDING TEMI TELEOP TASK!")
        # rmf_gateway().request_mode(robot_name="bed_responder", fleet_name="tinyRobot", mode=0)
        rmf_gateway().request_mode(
            robot_name="bed_responder", fleet_name="Temi", mode=0
        )
        return {"status": "teleop task ended"}
    else:
        return {"status": "Invalid Workflow"}

    service_id = await workflow.start_workflow()
    # asyncio.create_task(workflow.start_workflow())

    # asyncio.create_task(send_aw_service.add_sequences_and_start(send_aw_task))
    return {"status": "Workflow started", "service_id": service_id}


@router.post(
    "/dispatch_task",
    response_model=mdl.TaskDispatchResponseItem,
    responses={400: {"model": mdl.TaskDispatchResponseItem1}},
)
async def post_dispatch_task(
    request: mdl.DispatchTaskRequest = Body(...),
    task_repo: TaskRepository = Depends(task_repo_dep),
):
    resp = mdl.TaskDispatchResponse.parse_raw(
        await tasks_service().call(request.json(exclude_none=True))
    )
    if not resp.__root__.success:
        return RawJSONResponse(resp.json(), 400)
    task_state = cast(mdl.TaskDispatchResponseItem, resp.__root__).state
    await task_repo.save_task_state(task_state)
    await task_repo.save_task_request(task_state.booking.id, request.request)
    return resp.__root__


@router.post(
    "/robot_task",
    response_model=mdl.RobotTaskResponse,
    responses={400: {"model": mdl.RobotTaskResponse}},
)
async def post_robot_task(
    request: mdl.RobotTaskRequest = Body(...),
    task_repo: TaskRepository = Depends(task_repo_dep),
):
    resp = mdl.RobotTaskResponse.parse_raw(
        await tasks_service().call(request.json(exclude_none=True))
    )
    if not resp.__root__.__root__.success:
        return RawJSONResponse(resp.json(), 400)
    await task_repo.save_task_state(
        cast(mdl.TaskDispatchResponseItem, resp.__root__.__root__).state
    )
    return resp.__root__


@router.post("/interrupt_task", response_model=mdl.TaskInterruptionResponse)
async def post_interrupt_task(
    request: mdl.TaskInterruptionRequest = Body(...),
):
    return RawJSONResponse(await tasks_service().call(request.json(exclude_none=True)))


@router.post("/kill_task", response_model=mdl.TaskKillResponse)
async def post_kill_task(
    request: mdl.TaskKillRequest = Body(...),
):
    return RawJSONResponse(await tasks_service().call(request.json(exclude_none=True)))


@router.post("/resume_task", response_model=mdl.TaskResumeResponse)
async def post_resume_task(
    request: mdl.TaskResumeRequest = Body(...),
):
    return RawJSONResponse(await tasks_service().call(request.json(exclude_none=True)))


@router.post("/rewind_task", response_model=mdl.TaskRewindResponse)
async def post_rewind_task(
    request: mdl.TaskRewindRequest = Body(...),
):
    return RawJSONResponse(await tasks_service().call(request.json(exclude_none=True)))


@router.post("/skip_phase", response_model=mdl.SkipPhaseResponse)
async def post_skip_phase(
    request: mdl.TaskPhaseSkipRequest = Body(...),
):
    return RawJSONResponse(await tasks_service().call(request.json(exclude_none=True)))


@router.post("/task_discovery", response_model=mdl.TaskDiscovery)
async def post_task_discovery(
    request: mdl.TaskDiscoveryRequest = Body(...),
):
    return RawJSONResponse(await tasks_service().call(request.json(exclude_none=True)))


@router.post("/undo_skip_phase", response_model=mdl.UndoPhaseSkipResponse)
async def post_undo_skip_phase(
    request: mdl.UndoPhaseSkipRequest = Body(...),
):
    return RawJSONResponse(await tasks_service().call(request.json(exclude_none=True)))
