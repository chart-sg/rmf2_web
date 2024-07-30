# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Pose import Pose
from ..geometry_msgs.Vector3 import Vector3


class BoundingBox3D(pydantic.BaseModel):
    center: Pose = Pose()  # geometry_msgs/Pose
    size: Vector3 = Vector3()  # geometry_msgs/Vector3

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "center",
                "size",
            ],
        }


# # A 3D bounding box
#
# # The 3D position and orientation of the bounding box center
# geometry_msgs/Pose center
#
# # The total size of the bounding box, in meters, surrounding the object's center
# geometry_msgs/Vector3 size
