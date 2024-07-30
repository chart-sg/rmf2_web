# This is a generated file, do not edit

from typing import List

import pydantic


class LiftSelection_Response(pydantic.BaseModel):
    lift_assigned: str = ""  # string

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "lift_assigned",
            ],
        }


#
#
# # lift assigned
# string lift_assigned
