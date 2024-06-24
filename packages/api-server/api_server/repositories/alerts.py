import asyncio
from datetime import datetime
from typing import List, Optional

from fastapi import Depends

from api_server.authenticator import user_dep
from api_server.logger import logger
from api_server.models import User
from api_server.models import tortoise_models as ttm
from api_server.repositories.tasks import TaskRepository, task_repo_dep


class AlertRepository:
    def __init__(self, user: User, task_repo: Optional[TaskRepository]):
        self.user = user
        self.task_repo = (
            task_repo if task_repo is not None else TaskRepository(self.user)
        )

    async def get_all_alerts(self) -> List[ttm.AlertPydantic]:
        alerts = await ttm.Alert.all()
        return [await ttm.AlertPydantic.from_tortoise_orm(a) for a in alerts]

    async def alert_exists(self, alert_id: str) -> bool:
        result = await ttm.Alert.exists(id=alert_id)
        return result

    async def get_alert(self, alert_id: str) -> Optional[ttm.AlertPydantic]:
        alert = await ttm.Alert.get_or_none(id=alert_id)
        if alert is None:
            logger.error(f"Alert with ID {alert_id} not found")
            return None
        alert_pydantic = await ttm.AlertPydantic.from_tortoise_orm(alert)
        return alert_pydantic

    async def create_alert(
        self,
        alert_id: str,
        category: str,
        alert_type: str = None,
        service_id: str = None,
        robot_id: str = None,
        user_group: str = None,
        location: str = None,
        patient_id: str = None,
        other: str = None,
        message_action: str = None,
        user_action: str = None,
    ) -> Optional[ttm.AlertPydantic]:

        # get user_group from db via id
        # user_group_instance = None
        # if user_group:
        #     user_group_instance = await ttm.UserGroup.get(name=user_group)

        alert, _ = await ttm.Alert.update_or_create(
            {
                "original_id": alert_id,
                "category": category,
                "unix_millis_created_time": round(datetime.now().timestamp() * 1e3),
                "acknowledged_by": None,
                "unix_millis_acknowledged_time": None,
                "alert_type": alert_type,
                "service_id": service_id,
                "robot_id": robot_id,
                "location": location,
                "patient_id": patient_id,
                "other": other,
                "user_group": user_group,
                # "user_group": user_group_instance,
                "message_action": message_action,
                "user_action": user_action,
            },
            id=alert_id,
        )
        if alert is None:
            logger.error(f"Failed to create Alert with ID {alert_id}")
            return None
        alert_pydantic = await ttm.AlertPydantic.from_tortoise_orm(alert)
        return alert_pydantic

    async def reset_user_action(self, alert):

        await asyncio.sleep(30)
        logger.error(f"Complete snooze")
        alert.update_from_dict({"user_action": ""})
        await alert.save()

    async def snooze_alert(self, alert_id: str) -> Optional[ttm.AlertPydantic]:

        logger.error(f"Snoozing Alert with ID {alert_id}")
        alert = await ttm.Alert.get_or_none(id=alert_id)
        if alert is None:
            acknowledged_alert = await ttm.Alert.filter(original_id=alert_id).first()
            if acknowledged_alert is None:
                logger.error(f"No existing or past alert with ID {alert_id} found.")
                return None
            acknowledged_alert_pydantic = await ttm.AlertPydantic.from_tortoise_orm(
                acknowledged_alert
            )
            return acknowledged_alert_pydantic

        # Set user_action to 'snooze'
        alert.update_from_dict({"user_action": "snooze"})
        logger.error(f"Updating action to snooze for Alert with ID {alert_id}")
        await alert.save()

        # Reset user_action to '' after 30 seconds in separate thread
        asyncio.ensure_future(self.reset_user_action(alert))

        # Refetch the alert to ensure all fields are included.
        alert = await ttm.Alert.get(id=alert_id)

        alert_pydantic = await ttm.AlertPydantic.from_tortoise_orm(alert)
        return alert_pydantic

    async def acknowledge_alert(
        self, alert_id: str, user_action: str = None
    ) -> Optional[ttm.AlertPydantic]:
        if user_action == "snooze":
            return await self.snooze_alert(alert_id)

        alert = await ttm.Alert.get_or_none(id=alert_id)
        if alert is None:
            acknowledged_alert = await ttm.Alert.filter(original_id=alert_id).first()
            if acknowledged_alert is None:
                logger.error(f"No existing or past alert with ID {alert_id} found.")
                return None
            acknowledged_alert_pydantic = await ttm.AlertPydantic.from_tortoise_orm(
                acknowledged_alert
            )
            return acknowledged_alert_pydantic

        ack_time = datetime.now()
        epoch = datetime.utcfromtimestamp(0)
        ack_unix_millis = round((ack_time - epoch).total_seconds() * 1000)
        new_id = f"{alert_id}__{ack_unix_millis}"

        ack_alert = alert.clone(pk=new_id)
        # TODO(aaronchongth): remove the following line once we bump
        # tortoise-orm to include
        # https://github.com/tortoise/tortoise-orm/pull/1131. This is a
        # temporary workaround.
        ack_alert._custom_generated_pk = True  # pylint: disable=W0212
        unix_millis_acknowledged_time = round(ack_time.timestamp() * 1e3)
        ack_alert.update_from_dict(
            {
                "acknowledged_by": self.user.username,
                "unix_millis_acknowledged_time": unix_millis_acknowledged_time,
            }
        )

        if user_action:
            ack_alert.update_from_dict({"user_action": user_action})

        await ack_alert.save()

        # Save in logs who was the user that acknowledged the task
        # only do this if category = task
        if alert.category == alert.Category.Task:
            try:
                await self.task_repo.save_log_acknowledged_task_completion(
                    alert.id, self.user.username, unix_millis_acknowledged_time
                )
            except Exception as e:
                raise RuntimeError(
                    f"Error in save_log_acknowledged_task_completion {e}"
                ) from e

        await alert.delete()
        ack_alert_pydantic = await ttm.AlertPydantic.from_tortoise_orm(ack_alert)
        return ack_alert_pydantic


def alert_repo_dep(
    user: User = Depends(user_dep), task_repo: TaskRepository = Depends(task_repo_dep)
):
    return AlertRepository(user, task_repo)
