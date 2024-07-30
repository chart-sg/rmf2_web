# This is a generated file, do not edit

from typing import List

import pydantic

from ..rmf_lift_msgs.RobotForLift import RobotForLift


class LiftRobotMap(pydantic.BaseModel):
    lift_name: str = ""  # string
    robots: List[RobotForLift] = []  # rmf_lift_msgs/RobotForLift

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "lift_name",
                "robots",
            ],
        }


# string lift_name
#
# RobotForLift[] robots
