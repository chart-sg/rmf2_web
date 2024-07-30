# This is a generated file, do not edit

from typing import List

import pydantic


class RobotForLift(pydantic.BaseModel):
    session_id: str = ""  # string
    stage: pydantic.conint(ge=0, le=255) = 0  # uint8

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "session_id",
                "stage",
            ],
        }


# string session_id
#
# uint8 stage
# uint8 RSV=1
# uint8 ENT=2
# uint8 LIFT=3
# uint8 EXIT=4
