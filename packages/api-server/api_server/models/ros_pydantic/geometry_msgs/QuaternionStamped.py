# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Quaternion import Quaternion
from ..std_msgs.Header import Header


class QuaternionStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    quaternion: Quaternion = Quaternion()  # geometry_msgs/Quaternion

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "quaternion",
            ],
        }


# # This represents an orientation with reference coordinate frame and timestamp.
#
# std_msgs/Header header
# Quaternion quaternion
