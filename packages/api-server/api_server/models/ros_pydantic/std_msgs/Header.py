# This is a generated file, do not edit

from typing import List

import pydantic

from ..builtin_interfaces.Time import Time


class Header(pydantic.BaseModel):
    stamp: Time = Time()  # builtin_interfaces/Time
    frame_id: str = ""  # string

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "stamp",
                "frame_id",
            ],
        }


# # Standard metadata for higher-level stamped data types.
# # This is generally used to communicate timestamped data
# # in a particular coordinate frame.
#
# # Two-integer timestamp that is expressed as seconds and nanoseconds.
# builtin_interfaces/Time stamp
#
# # Transform frame with which this data is associated.
# string frame_id
