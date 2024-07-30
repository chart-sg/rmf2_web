# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Point32 import Point32


class BoundingBox8P(pydantic.BaseModel):
    points: pydantic.conlist(
        item_type=Point32, min_items=8, max_items=8
    ) = []  # geometry_msgs/Point32

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "points",
            ],
        }


# # Array of Point32 (x,y,z) to represent 3D cooridinates for 8 points of a 3D bounding box
# geometry_msgs/Point32[8] points
