# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.TwistWithCovariance import TwistWithCovariance
from ..std_msgs.Header import Header


class TwistWithCovarianceStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    twist: TwistWithCovariance = (
        TwistWithCovariance()
    )  # geometry_msgs/TwistWithCovariance

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "twist",
            ],
        }


# # This represents an estimated twist with reference coordinate frame and timestamp.
#
# std_msgs/Header header
# TwistWithCovariance twist
