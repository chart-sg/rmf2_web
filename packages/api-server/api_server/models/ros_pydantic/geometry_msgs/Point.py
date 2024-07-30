# This is a generated file, do not edit

from typing import List

import pydantic


class Point(pydantic.BaseModel):
    x: float = 0  # float64
    y: float = 0  # float64
    z: float = 0  # float64

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "x",
                "y",
                "z",
            ],
        }


# # This contains the position of a point in free space
# float64 x
# float64 y
# float64 z
