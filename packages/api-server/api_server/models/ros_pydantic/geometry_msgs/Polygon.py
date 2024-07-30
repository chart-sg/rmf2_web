# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Point32 import Point32


class Polygon(pydantic.BaseModel):
    points: List[Point32] = []  # geometry_msgs/Point32

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "points",
            ],
        }


# # A specification of a polygon where the first and last points are assumed to be connected
#
# Point32[] points
