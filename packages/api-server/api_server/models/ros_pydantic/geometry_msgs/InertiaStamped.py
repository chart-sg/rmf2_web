# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Inertia import Inertia
from ..std_msgs.Header import Header


class InertiaStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    inertia: Inertia = Inertia()  # geometry_msgs/Inertia

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "inertia",
            ],
        }


# # An Inertia with a time stamp and reference frame.
#
# std_msgs/Header header
# Inertia inertia
