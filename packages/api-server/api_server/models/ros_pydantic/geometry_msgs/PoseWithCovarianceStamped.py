# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.PoseWithCovariance import PoseWithCovariance
from ..std_msgs.Header import Header


class PoseWithCovarianceStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    pose: PoseWithCovariance = PoseWithCovariance()  # geometry_msgs/PoseWithCovariance

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "pose",
            ],
        }


# # This expresses an estimated pose with a reference coordinate frame and timestamp
#
# std_msgs/Header header
# PoseWithCovariance pose
