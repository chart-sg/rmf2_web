# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Point import Point
from ..std_msgs.Header import Header


class PointStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    point: Point = Point()  # geometry_msgs/Point

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "point",
            ],
        }


# # This represents a Point with reference coordinate frame and timestamp
#
# std_msgs/Header header
# Point point
