# This is a generated file, do not edit

from typing import List

import pydantic


class LiftZoneRequest(pydantic.BaseModel):
    session_id: str = ""  # string
    request_type: pydantic.conint(ge=0, le=255) = 0  # uint8
    lift_option: List[str] = []  # string

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "session_id",
                "request_type",
                "lift_option",
            ],
        }


# string session_id
#
# uint8 request_type
# uint8 ENTRY=1
# uint8 END=2
#
# # lift option to choose
# string[] lift_option
