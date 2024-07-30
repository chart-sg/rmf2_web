# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Wrench import Wrench
from ..std_msgs.Header import Header


class WrenchStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    wrench: Wrench = Wrench()  # geometry_msgs/Wrench

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "wrench",
            ],
        }


# # A wrench with reference coordinate frame and timestamp
#
# std_msgs/Header header
# Wrench wrench
