# This is a generated file, do not edit

from typing import List

import pydantic


class ColorRGBA(pydantic.BaseModel):
    r: float = 0  # float32
    g: float = 0  # float32
    b: float = 0  # float32
    a: float = 0  # float32

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "r",
                "g",
                "b",
                "a",
            ],
        }


# float32 r
# float32 g
# float32 b
# float32 a
