# This is a generated file, do not edit

from typing import List

import pydantic


class MultiArrayDimension(pydantic.BaseModel):
    label: str = ""  # string
    size: pydantic.conint(ge=0, le=4294967295) = 0  # uint32
    stride: pydantic.conint(ge=0, le=4294967295) = 0  # uint32

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "label",
                "size",
                "stride",
            ],
        }


# # This was originally provided as an example message.
# # It is deprecated as of Foxy
# # It is recommended to create your own semantically meaningful message.
# # However if you would like to continue using this please use the equivalent in example_msgs.
#
# string label   # label of given dimension
# uint32 size    # size of given dimension (in type units)
# uint32 stride  # stride of given dimension
