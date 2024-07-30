# This is a generated file, do not edit

from typing import List

import pydantic


class Int64(pydantic.BaseModel):
    data: int = 0  # int64

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "data",
            ],
        }


# # This was originally provided as an example message.
# # It is deprecated as of Foxy
# # It is recommended to create your own semantically meaningful message.
# # However if you would like to continue using this please use the equivalent in example_msgs.
#
# int64 data
