# This is a generated file, do not edit

from typing import List

import pydantic


class Quaternion(pydantic.BaseModel):
    x: float = 0  # float64
    y: float = 0  # float64
    z: float = 0  # float64
    w: float = 0  # float64

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "x",
                "y",
                "z",
                "w",
            ],
        }


# # This represents an orientation in free space in quaternion form.
#
# float64 x 0
# float64 y 0
# float64 z 0
# float64 w 1
