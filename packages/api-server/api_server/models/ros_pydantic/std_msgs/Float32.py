# This is a generated file, do not edit

from typing import List

import pydantic


class Float32(pydantic.BaseModel):
    data: float = 0  # float32

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
# float32 data
