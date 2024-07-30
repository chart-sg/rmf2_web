# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Point import Point
from ..geometry_msgs.Quaternion import Quaternion


class Pose(pydantic.BaseModel):
    position: Point = Point()  # geometry_msgs/Point
    orientation: Quaternion = Quaternion()  # geometry_msgs/Quaternion

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "position",
                "orientation",
            ],
        }


# # A representation of pose in free space, composed of position and orientation.
#
# Point position
# Quaternion orientation
