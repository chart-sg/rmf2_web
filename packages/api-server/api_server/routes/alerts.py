from enum import Enum
from typing import List

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from reactivex import operators as rxops

from api_server.fast_io import FastIORouter, SubscriptionRequest
from api_server.models import tortoise_models as ttm
from api_server.repositories import AlertRepository, alert_repo_dep
from api_server.rmf_io import alert_events

router = FastIORouter(tags=["Alerts"])


@router.sub("", response_model=ttm.AlertPydantic)
async def sub_alerts(_req: SubscriptionRequest):
    return alert_events.alerts.pipe(rxops.filter(lambda x: x is not None))


@router.get("", response_model=List[ttm.AlertPydantic])
async def get_alerts(repo: AlertRepository = Depends(alert_repo_dep)):
    return await repo.get_all_alerts()


@router.get("/{alert_id}", response_model=ttm.AlertPydantic)
async def get_alert(alert_id: str, repo: AlertRepository = Depends(alert_repo_dep)):
    alert = await repo.get_alert(alert_id)
    if alert is None:
        raise HTTPException(404, f"Alert with ID {alert_id} not found")
    return alert


class AlertPayload(BaseModel):
    alert_type: str = None
    service_id: str = None
    robot_id: str = None
    user_group: str = None
    other: str = None
    message_action: str = None


@router.post("", status_code=201, response_model=ttm.AlertPydantic)
async def create_alert(
    alert_id: str,
    category: str,
    # user_group: str = None,
    body: AlertPayload = None,
    repo: AlertRepository = Depends(alert_repo_dep),
):
    # message = body.message if body and body.message else None
    # message_action = body.message_action if body and body.message_action else None

    alert = await repo.create_alert(
        alert_id=alert_id,
        category=category,
        alert_type=body.alert_type,
        service_id=body.service_id,
        robot_id=body.robot_id,
        user_group=body.user_group,
        other=body.other,
    )

    if alert is None:
        raise HTTPException(404, f"Could not create alert with ID {alert_id}")
    return alert


class ActionType(Enum):
    accept = "accept"
    reject = "reject"
    ignore = "ignore"
    acknowledge = "acknowledge"
    snooze = "snooze"
    unacknowledge = "unacknowledge"


class AlertAction(BaseModel):
    alert_id: str
    action: ActionType


@router.put("", status_code=201, response_model=ttm.AlertPydantic)
async def update_alert(
    body: AlertAction,
    repo: AlertRepository = Depends(alert_repo_dep),
):
    # message = body.message if body and body.message else None
    # message_action = body.message_action if body and body.message_action else None

    alert = await repo.acknowledge_alert(
        alert_id=body.alert_id, user_action=body.action.value
    )

    if alert is None:
        raise HTTPException(404, f"Could not update alert with ID {body.alert_id}")
    alert_events.alerts.on_next(alert)
    return alert


@router.post("/{alert_id}", status_code=201, response_model=ttm.AlertPydantic)
async def acknowledge_alert(
    alert_id: str, repo: AlertRepository = Depends(alert_repo_dep)
):
    alert = await repo.acknowledge_alert(alert_id)
    if alert is None:
        raise HTTPException(404, f"Could not acknowledge alert with ID {alert_id}")
    alert_events.alerts.on_next(alert)
    return alert


@router.delete("", status_code=201)
async def delete_alerts(repo: AlertRepository = Depends(alert_repo_dep)):
    alert = await repo.delete_alerts()
    if alert is None:
        raise HTTPException(404, f"Could not delete alerts")
    return {"status": "Alerts deleted"}
