# This is a generated file, do not edit

from typing import List

import pydantic

from ..rmf_lift_msgs.LiftRobotMap import LiftRobotMap


class LiftZoneState(pydantic.BaseModel):
    lift_robot_maps: List[LiftRobotMap] = []  # rmf_lift_msgs/LiftRobotMap

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "lift_robot_maps",
            ],
        }


# #   uint8 lift_zone_id
# #   uint8 free_entry_qty
#
# LiftRobotMap[] lift_robot_maps
