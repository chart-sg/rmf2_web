# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Accel import Accel


class AccelWithCovariance(pydantic.BaseModel):
    accel: Accel = Accel()  # geometry_msgs/Accel
    covariance: pydantic.conlist(
        item_type=float, min_items=36, max_items=36
    ) = []  # float64

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "accel",
                "covariance",
            ],
        }


# # This expresses acceleration in free space with uncertainty.
#
# Accel accel
#
# # Row-major representation of the 6x6 covariance matrix
# # The orientation parameters use a fixed-axis representation.
# # In order, the parameters are:
# # (x, y, z, rotation about X axis, rotation about Y axis, rotation about Z axis)
# float64[36] covariance
