# This is a generated file, do not edit

from typing import List

import pydantic

from ..std_msgs.MultiArrayLayout import MultiArrayLayout


class Float32MultiArray(pydantic.BaseModel):
    layout: MultiArrayLayout = MultiArrayLayout()  # std_msgs/MultiArrayLayout
    data: List[float] = []  # float32

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "layout",
                "data",
            ],
        }


# # This was originally provided as an example message.
# # It is deprecated as of Foxy
# # It is recommended to create your own semantically meaningful message.
# # However if you would like to continue using this please use the equivalent in example_msgs.
#
# # Please look at the MultiArrayLayout message definition for
# # documentation on all multiarrays.
#
# MultiArrayLayout  layout        # specification of data layout
# float32[]         data          # array of data