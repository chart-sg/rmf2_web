# This is a generated file, do not edit

from typing import List

import pydantic


class LiftChange(pydantic.BaseModel):
    robot_name: str = ""  # string
    lift_name: str = ""  # string
    level_name: str = ""  # string

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "robot_name",
                "lift_name",
                "level_name",
            ],
        }


# string robot_name
# string lift_name
# string level_name
