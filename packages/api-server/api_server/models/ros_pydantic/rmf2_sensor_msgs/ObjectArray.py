# This is a generated file, do not edit

from typing import List

import pydantic

from ..rmf2_sensor_msgs.Object import Object


class ObjectArray(pydantic.BaseModel):
    source: str = ""  # string
    object_array: List[Object] = []  # rmf2_sensor_msgs/Object

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "source",
                "object_array",
            ],
        }


# # Unique identifier to Traffic-editor sensor
# string source
#
# # Array for objects
# Object[] object_array
