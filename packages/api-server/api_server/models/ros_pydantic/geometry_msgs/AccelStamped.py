# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Accel import Accel
from ..std_msgs.Header import Header


class AccelStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    accel: Accel = Accel()  # geometry_msgs/Accel

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "accel",
            ],
        }


# # An accel with reference coordinate frame and timestamp
# std_msgs/Header header
# Accel accel
