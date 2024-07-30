# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Polygon import Polygon
from ..std_msgs.Header import Header


class PolygonStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    polygon: Polygon = Polygon()  # geometry_msgs/Polygon

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "polygon",
            ],
        }


# # This represents a Polygon with reference coordinate frame and timestamp
#
# std_msgs/Header header
# Polygon polygon
