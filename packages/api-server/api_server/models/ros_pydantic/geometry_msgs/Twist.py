# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Vector3 import Vector3


class Twist(pydantic.BaseModel):
    linear: Vector3 = Vector3()  # geometry_msgs/Vector3
    angular: Vector3 = Vector3()  # geometry_msgs/Vector3

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "linear",
                "angular",
            ],
        }


# # This expresses velocity in free space broken into its linear and angular parts.
#
# Vector3  linear
# Vector3  angular
