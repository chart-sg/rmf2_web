from enum import Enum

from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.fields import BigIntField, CharEnumField, CharField, ForeignKeyField
from tortoise.models import Model


class Alert(Model):
    """
    General alert that can be triggered by events.
    """

    class Category(str, Enum):
        Default = "default"
        Task = "task"
        Fleet = "fleet"
        Robot = "robot"

    id = CharField(255, pk=True)
    original_id = CharField(255, index=True)
    category = CharEnumField(Category, index=True)
    unix_millis_created_time = BigIntField(null=False, index=True)
    acknowledged_by = CharField(255, null=True, index=True)
    unix_millis_acknowledged_time = BigIntField(null=True, index=True)
    message = CharField(255, null=True, index=True)
    user_group: ForeignKeyField = ForeignKeyField(
        "models.UserGroup", related_name="alerts", null=True
    )
    message_action = CharField(255, null=True, index=False)
    user_action = CharField(255, null=True, index=False)


AlertPydantic = pydantic_model_creator(Alert)
