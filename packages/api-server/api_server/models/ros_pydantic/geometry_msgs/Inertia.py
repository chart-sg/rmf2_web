# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Vector3 import Vector3


class Inertia(pydantic.BaseModel):
    m: float = 0  # float64
    com: Vector3 = Vector3()  # geometry_msgs/Vector3
    ixx: float = 0  # float64
    ixy: float = 0  # float64
    ixz: float = 0  # float64
    iyy: float = 0  # float64
    iyz: float = 0  # float64
    izz: float = 0  # float64

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "m",
                "com",
                "ixx",
                "ixy",
                "ixz",
                "iyy",
                "iyz",
                "izz",
            ],
        }


# # Mass [kg]
# float64 m
#
# # Center of mass [m]
# geometry_msgs/Vector3 com
#
# # Inertia Tensor [kg-m^2]
# #     | ixx ixy ixz |
# # I = | ixy iyy iyz |
# #     | ixz iyz izz |
# float64 ixx
# float64 ixy
# float64 ixz
# float64 iyy
# float64 iyz
# float64 izz
