# This is a generated file, do not edit

from typing import List

import pydantic

from ..builtin_interfaces.Time import Time


class SensorTrigger(pydantic.BaseModel):
    name: str = ""  # string
    source: str = ""  # string
    timestamp: Time = Time()  # builtin_interfaces/Time
    trigger: str = ""  # string
    publish_rate: str = ""  # string
    publish_period: str = ""  # string

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "name",
                "source",
                "timestamp",
                "trigger",
                "publish_rate",
                "publish_period",
            ],
        }


# # Unique identifier of this sensor adapter
# string name
#
# # Unique identifier to Traffic-editor sensor
# string source
#
# # Time when this msg is created
# builtin_interfaces/Time timestamp
#
# # Trigger to start or stop sensor and check status (Start, Stop, Debug)
# string trigger
#
# # New publish_rate for sensor (In seconds, for e.g 2 means every 2 second publish once, if empty then will be default rate)
# string publish_rate
#
# # How long to publish for (In seconds, if empty then will be continous publishing)
# string publish_period
