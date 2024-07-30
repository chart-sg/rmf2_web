# This is a generated file, do not edit

from typing import List

import pydantic

from ..geometry_msgs.Transform import Transform
from ..std_msgs.Header import Header


class TransformStamped(pydantic.BaseModel):
    header: Header = Header()  # std_msgs/Header
    child_frame_id: str = ""  # string
    transform: Transform = Transform()  # geometry_msgs/Transform

    class Config:
        orm_mode = True
        schema_extra = {
            "required": [
                "header",
                "child_frame_id",
                "transform",
            ],
        }


# # This expresses a transform from coordinate frame header.frame_id
# # to the coordinate frame child_frame_id at the time of header.stamp
# #
# # This message is mostly used by the
# # <a href="https://index.ros.org/p/tf2/">tf2</a> package.
# # See its documentation for more information.
# #
# # The child_frame_id is necessary in addition to the frame_id
# # in the Header to communicate the full reference for the transform
# # in a self contained message.
#
# # The frame id in the header is used as the reference frame of this transform.
# std_msgs/Header header
#
# # The frame id of the child frame to which this transform points.
# string child_frame_id
#
# # Translation and rotation in 3-dimensions of child_frame_id from header.frame_id.
# Transform transform
