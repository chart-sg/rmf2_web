# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Vector3 import Vector3
from ..std_msgs.Header import Header


class Vector3Stamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    vector: Vector3 = Vector3()  # geometry_msgs/Vector3

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "vector",
            ],
        }


# # This represents a Vector3 with reference coordinate frame and timestamp
#
# # Note that this follows vector semantics with it always anchored at the origin,
# # so the rotational elements of a transform are the only parts applied when transforming.
#
# std_msgs/Header header
# Vector3 vector
