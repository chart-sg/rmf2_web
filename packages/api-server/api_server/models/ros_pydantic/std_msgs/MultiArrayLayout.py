# This is a generated file, do not edit

from typing import List

import pydantic

from ..std_msgs.MultiArrayDimension import MultiArrayDimension


class MultiArrayLayout(pydantic.BaseModel):
    dim: List[MultiArrayDimension] = []  # std_msgs/MultiArrayDimension
    data_offset: pydantic.conint(ge=0, le=4294967295) = 0  # uint32

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "dim",
                "data_offset",
            ],
        }


# # This was originally provided as an example message.
# # It is deprecated as of Foxy
# # It is recommended to create your own semantically meaningful message.
# # However if you would like to continue using this please use the equivalent in example_msgs.
#
# # The multiarray declares a generic multi-dimensional array of a
# # particular data type.  Dimensions are ordered from outer most
# # to inner most.
# #
# # Accessors should ALWAYS be written in terms of dimension stride
# # and specified outer-most dimension first.
# #
# # multiarray(i,j,k) = data[data_offset + dim_stride[1]*i + dim_stride[2]*j + k]
# #
# # A standard, 3-channel 640x480 image with interleaved color channels
# # would be specified as:
# #
# # dim[0].label  = "height"
# # dim[0].size   = 480
# # dim[0].stride = 3*640*480 = 921600  (note dim[0] stride is just size of image)
# # dim[1].label  = "width"
# # dim[1].size   = 640
# # dim[1].stride = 3*640 = 1920
# # dim[2].label  = "channel"
# # dim[2].size   = 3
# # dim[2].stride = 3
# #
# # multiarray(i,j,k) refers to the ith row, jth column, and kth channel.
#
# MultiArrayDimension[] dim # Array of dimension properties
# uint32 data_offset        # padding bytes at front of data
