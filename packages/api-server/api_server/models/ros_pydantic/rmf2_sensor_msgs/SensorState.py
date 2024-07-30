# This is a generated file, do not edit

from typing import List

import pydantic

from ..builtin_interfaces.Time import Time


class SensorState(pydantic.BaseModel):
    name: str = ""  # string
    source: str = ""  # string
    timestamp: Time = Time()  # builtin_interfaces/Time
    adapter_type: str = ""  # string
    msg_type: str = ""  # string
    default_publish_rate: str = ""  # string
    current_publish_rate: str = ""  # string
    sensor_flag: str = ""  # string

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "name",
                "source",
                "timestamp",
                "adapter_type",
                "msg_type",
                "default_publish_rate",
                "current_publish_rate",
                "sensor_flag",
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
# # Type of sensor adapter (constant/trigger)
# string adapter_type
#
# # Type of message (Objects)
# string msg_type
#
# # Rate of publishing for sensor adapter, default from config file
# string default_publish_rate
#
# # Rate of publishing for sensor adapter that is currently used
# string current_publish_rate
#
# # Whether the sensor is publishing or on standby (Publishing / Standby)
# string sensor_flag
