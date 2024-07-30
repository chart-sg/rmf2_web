# This is a generated file, do not edit

from typing import List

import pydantic

from ..builtin_interfaces.Duration import Duration
from ..builtin_interfaces.Time import Time
from ..rmf2_sensor_msgs.BoundingBox3D import BoundingBox3D
from ..rmf2_sensor_msgs.BoundingBox8P import BoundingBox8P


class Object(pydantic.BaseModel):
    source: str = ""  # string
    timestamp: Time = Time()  # builtin_interfaces/Time
    classification: str = ""  # string
    reference: str = ""  # string
    bbox_3d: BoundingBox3D = BoundingBox3D()  # rmf2_sensor_msgs/BoundingBox3D
    bbox_8p: BoundingBox8P = BoundingBox8P()  # rmf2_sensor_msgs/BoundingBox8P
    direction: str = ""  # string
    level: str = ""  # string
    lifetime: Duration = Duration()  # builtin_interfaces/Duration

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "source",
                "timestamp",
                "classification",
                "reference",
                "bbox_3d",
                "bbox_8p",
                "direction",
                "level",
                "lifetime",
            ],
        }


# # Unique identifier to Traffic-editor sensor
# string source
#
# # Time when this object is detected
# builtin_interfaces/Time timestamp
#
# # Classification label for object type (eg. obstacle, patient, human, bed, wheelchair)
# string classification
#
# # Reference point is local or global
# string reference
#
# # Size of 3D Bounding box
# BoundingBox3D bbox_3d
#
# # 8 corners of 3D Bounding box
# BoundingBox8P bbox_8p
#
# # Which direction is the object moving(eg. left, right, center, exit_left, exit_right)
# string direction
#
# # What level if the RMF map is the object at
# string level
#
# # The expected lifetime of the object
# builtin_interfaces/Duration lifetime
