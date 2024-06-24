import asyncio

from api_server.logger import logger
from api_server.rmf_io.rmf2_service_sequence import (
    Rmf2Service,
    SequenceNotification,
    SequenceRoboticTask,
    SequenceTemiTask,
)


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id: str, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class TestFlow:
    def __init__(self, body):
        self.robot_id = body.data.robot_id
        self.location = body.data.location
        self.robot_fleet = (
            body.data.robot_fleet if body.data.robot_fleet is not None else "all"
        )
        self.zone_type = (
            [body.data.zone_type] if body.data.zone_type is not None else "all"
        )

        self.data = body.data
        self.userId = body.requester
        self.senderGroup = body.requester_group
        self.receiverGroup = body.receiver_group

    async def start_workflow(self):

        # Harcode temi
        temi_robot = "bed_responder"
        temi_fleet = "Temi"
        temi_charger = "temi_charger"
        temi_location = "bed_entry"
        temi_zone_location = "bed_2"

        # Harcode pudu
        pudu_robot = "pudubot2"
        pudu_fleet = "pudubot2"
        pudu_charger = "blanki_charger"
        pudu_location = "comfort_2"
        pudu_zone_location = "comfort_2_entry"

        # Harcode pudu
        aw_robot = "piimo_1"
        aw_fleet = "piimo"
        aw_charger = "piimo_charger"
        aw_location = "consultation_entry"
        aw_zone_location = "ff"

        # Create a service
        test_chart_service = Rmf2Service(name="test_chart")

        temi_place_data = {
            "category": "go_to_place",
            "start": temi_location,
            "robot": temi_robot,
            "fleet": temi_fleet,
        }

        send_temi = SequenceRoboticTask(
            name="test_temi", serviceId=test_chart_service.id, data=temi_place_data
        )

        temi_zone_data = {
            "category": "zone",
            "start": temi_zone_location,
            "robot": temi_robot,
            "fleet": temi_fleet,
            "zoneType": "left",
        }

        send_temi_zone = SequenceRoboticTask(
            name="test_temi_zone", serviceId=test_chart_service.id, data=temi_zone_data
        )

        pudu_data = {
            "category": "zone",
            "start": self.location,
            "robot": pudu_robot,
            "fleet": pudu_fleet,
            "zoneType": self.zone_type,
            "zoneFacing": 90,
            "delay": 5,
        }
        send_pudu = SequenceRoboticTask(
            name="test_pudu", serviceId=test_chart_service.id, data=pudu_data
        )

        aw_data = {
            "category": "zone",
            "start": aw_zone_location,
            "robot": aw_robot,
            "fleet": aw_fleet,
            "zoneType": self.zone_type,
            "zoneFacing": 180,
        }
        send_aw = SequenceRoboticTask(
            name="test_aw", serviceId=test_chart_service.id, data=aw_data
        )

        aw_goal_data = {
            "category": "go_to_place",
            "start": aw_location,
            "robot": aw_robot,
            "fleet": aw_fleet,
        }
        send_goal_aw = SequenceRoboticTask(
            name="test_goal_aw", serviceId=test_chart_service.id, data=aw_goal_data
        )

        test_chart_service.tasks = [send_goal_aw, send_aw]

        try:
            asyncio.create_task(test_chart_service.start())
            # await send_aw_service.start()

        except RobotDispatchFailed as e:
            logger.error(f"send temi service failed: {e}")

        return test_chart_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
