# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Pose import Pose
from ..std_msgs.Header import Header


class PoseStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    pose: Pose = Pose()  # geometry_msgs/Pose

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "pose",
            ],
        }


# # A Pose with reference coordinate frame and timestamp
#
# std_msgs/Header header
# Pose pose
