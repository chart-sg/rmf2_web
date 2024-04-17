from tortoise.fields.data import BooleanField, CharField
from tortoise.fields.relational import (
    ForeignKeyField,
    ManyToManyField,
    ManyToManyRelation,
    ReverseRelation,
)
from tortoise.models import Model

from .alerts import Alert
from .authorization import Role


class User(Model):
    username: str = CharField(255, pk=True)  # type: ignore
    is_admin: bool = BooleanField()  # type: ignore
    roles: ManyToManyRelation[Role] = ManyToManyField("models.Role")
    user_group: ForeignKeyField = ForeignKeyField(
        "models.UserGroup", related_name="users", null=True
    )


class UserGroup(Model):
    name: str = CharField(255, pk=True)  # type: ignore
    users: ReverseRelation["User"]
    alerts: ReverseRelation["Alert"]
