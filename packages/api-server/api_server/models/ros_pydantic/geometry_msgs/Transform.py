# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Quaternion import Quaternion
from ..geometry_msgs.Vector3 import Vector3


class Transform(pydantic.BaseModel):
    translation: Vector3 = Vector3()  # geometry_msgs/Vector3
    rotation: Quaternion = Quaternion()  # geometry_msgs/Quaternion

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "translation",
                "rotation",
            ],
        }


# # This represents the transform between two coordinate frames in free space.
#
# Vector3 translation
# Quaternion rotation
