# This is a generated file, do not edit

from typing import List

import pydantic


class RobotCost(pydantic.BaseModel):
    robot_name: str = ""  # string
    cost: float = 0  # float32
    robot_task: str = ""  # string
    response: pydantic.conint(ge=0, le=255) = 0  # uint8

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "robot_name",
                "cost",
                "robot_task",
                "response",
            ],
        }


# string robot_name
#
# # The cost to travel to waypoint
# float32 cost
#
# # The task that robot is doing, empty if no task
# string robot_task
#
# # The response status given the request msg
# uint8 response
# uint8 INVALID=0
# uint8 VALID=1
# uint8 NO_WAYPOINT=2
# uint8 WRONG_WAYPOINT=3
# uint8 WRONG_ROBOT=4
# uint8 NO_VALID_PATH=5
