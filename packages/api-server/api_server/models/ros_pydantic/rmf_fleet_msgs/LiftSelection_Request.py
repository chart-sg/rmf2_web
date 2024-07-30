# This is a generated file, do not edit

from typing import List

import pydantic


class LiftSelection_Request(pydantic.BaseModel):
    lift_zone_name: str = ""  # string
    lift_option: List[str] = []  # string

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "lift_zone_name",
                "lift_option",
            ],
        }


# string lift_zone_name
#
# # lift option to choose
# string[] lift_option
#
