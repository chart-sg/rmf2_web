# This is a generated file, do not edit

from typing import List

import pydantic


class Point32(pydantic.BaseModel):
    x: float = 0  # float32
    y: float = 0  # float32
    z: float = 0  # float32

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "x",
                "y",
                "z",
            ],
        }


# # This contains the position of a point in free space(with 32 bits of precision).
# # It is recommended to use Point wherever possible instead of Point32.
# #
# # This recommendation is to promote interoperability.
# #
# # This message is designed to take up less space when sending
# # lots of points at once, as in the case of a PointCloud.
#
# float32 x
# float32 y
# float32 z
