from typing import List

from pydantic import BaseModel

from .ros_pydantic import rmf2_sensor_msgs


class ObjectZone(rmf2_sensor_msgs.Object):
    zones: List[str]
