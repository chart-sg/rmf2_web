# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Vector3 import Vector3


class Wrench(pydantic.BaseModel):
    force: Vector3 = Vector3()  # geometry_msgs/Vector3
    torque: Vector3 = Vector3()  # geometry_msgs/Vector3

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "force",
                "torque",
            ],
        }


# # This represents force in free space, separated into its linear and angular parts.
#
# Vector3  force
# Vector3  torque
