# This is a generated file, do not edit

from typing import List

import pydantic


class Vector3(pydantic.BaseModel):
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


# # This represents a vector in free space.
#
# # This is semantically different than a point.
# # A vector is always anchored at the origin.
# # When a transform is applied to a vector, only the rotational component is applied.
#
# float64 x
# float64 y
# float64 z
