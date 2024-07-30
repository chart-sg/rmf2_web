# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Pose import Pose
from ..std_msgs.Header import Header


class PoseArray(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    poses: List[Pose] = []  # geometry_msgs/Pose

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "poses",
            ],
        }


# # An array of poses with a header for global reference.
#
# std_msgs/Header header
#
# Pose[] poses
