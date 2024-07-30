# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Twist import Twist


class TwistWithCovariance(pydantic.BaseModel):
    twist: Twist = Twist()  # geometry_msgs/Twist
    covariance: pydantic.conlist(
        item_type=float, min_items=36, max_items=36
    ) = []  # float64

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "twist",
                "covariance",
            ],
        }


# # This expresses velocity in free space with uncertainty.
#
# Twist twist
#
# # Row-major representation of the 6x6 covariance matrix
# # The orientation parameters use a fixed-axis representation.
# # In order, the parameters are:
# # (x, y, z, rotation about X axis, rotation about Y axis, rotation about Z axis)
# float64[36] covariance
