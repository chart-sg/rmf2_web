# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Twist import Twist
from ..std_msgs.Header import Header


class TwistStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    twist: Twist = Twist()  # geometry_msgs/Twist

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "twist",
            ],
        }


# # A twist with reference coordinate frame and timestamp
#
# std_msgs/Header header
# Twist twist
