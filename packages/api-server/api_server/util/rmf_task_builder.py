# rmf_task_builder.py
import json
import math

from api_server.ros import ros_node as default_ros_node


def rmfTaskBuilder(
    robot: str,
    fleet: str,
    category: str,
    start: str,
    zoneType: list[str] = ["all"],
    startTime: int = 0,
    zoneFacing: int = None,
):
    payload = {}
    if fleet and robot:
        payload["type"] = "robot_task_request"
        payload["robot"] = robot
        payload["fleet"] = fleet
    else:
        payload["type"] = "dispatch_task_request"

    request = {}

    now = default_ros_node().get_clock().now().to_msg()
    now.sec = now.sec + startTime
    start_time = now.sec * 1000 + round(now.nanosec / 10**6)
    request["unix_millis_earliest_start_time"] = start_time

    request["category"] = "compose"

    description = {}
    description["category"] = category
    description["phases"] = []

    activities = []

    # either gotoplace or gotozone
    if category == "go_to_place":
        # activities.append({
        #     "category": "go_to_place",
        #     "description": start,
        #     "orientation": math.radians(zoneFacing) if zoneFacing else None})

        # activities.append({
        #     "category": "go_to_place",
        #     "description": {
        #         "waypoint": start,
        #         "orientation": math.radians(zoneFacing) if zoneFacing else None}
        #     })

        desc = {"waypoint": start}
        if zoneFacing:
            desc["orientation"] = math.radians(zoneFacing)

        activities.append({"category": "go_to_place", "description": desc})

    elif category == "teleop":
        activities.append(
            {
                "category": "perform_action",
                "description": {
                    "unix_millis_action_duration_estimate": 60000,
                    "category": "teleop",
                    "description": {},
                },
            }
        )

    elif category == "zone":
        # if "aw" in robot:
        #     activities.append({"category": "go_to_place", "description": f"{start}_entry"})

        seq_dict = {
            "category": "zone",
            "description": {
                "zone": start,
                "types": zoneType,
                "facing": math.radians(zoneFacing) if zoneFacing else None,
            },
        }

        # if zoneFacing:
        #     seq_dict["facing"] = math.radians(zoneFacing)

        activities.append(seq_dict)

        # activities.append(
        #     {
        #         "category": "perform_action",
        #         "description": {
        #             "unix_millis_action_duration_estimate": 60000,
        #             "category": "teleop",
        #             "description": {},
        #         },
        #     }
        # )

    # if category == 'teleop':
    #     activities.append(
    #         {
    #             "category": "perform_action",
    #             "description": {
    #                 "unix_millis_action_duration_estimate": 60000,
    #                 "category": "teleop",
    #                 "description": {},
    #             }
    #         }
    #     )

    description["phases"].append(
        {
            "activity": {
                "category": "sequence",
                "description": {"activities": activities},
            }
        }
    )
    request["description"] = description
    payload["request"] = request

    return json.dumps(payload)
