# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.AccelWithCovariance import AccelWithCovariance
from ..std_msgs.Header import Header


class AccelWithCovarianceStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    accel: AccelWithCovariance = (
        AccelWithCovariance()
    )  # geometry_msgs/AccelWithCovariance

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "accel",
            ],
        }


# # This represents an estimated accel with reference coordinate frame and timestamp.
# std_msgs/Header header
# AccelWithCovariance accel
