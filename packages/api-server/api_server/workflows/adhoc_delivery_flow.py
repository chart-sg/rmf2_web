import asyncio

from api_server.app_config import app_config
from api_server.logger import logger
from api_server.rmf_io.rmf2_service_sequence import (
    Rmf2Service,
    SequenceNotification,
    SequencePuduTask,
    SequenceRoboticTask,
)
from api_server.rmf_io.state_monitor import stateMonitor


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id: str, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class AdhocDeliveryFlow:
    def __init__(self, body):
        self.sm = stateMonitor()
        # self.service_id = body.service_id
        self.robot_id = body.data.robot_id
        self.robot_fleet = body.data.robot_fleet
        self.location = body.data.location
        self.zone_type = (
            [body.data.zone_type] if body.data.zone_type is not None else "bottom"
        )

        self.data = body.data
        self.userId = body.requester
        self.senderGroup = body.requester_group
        self.receiverGroup = body.receiver_group
        self.items = body.data.items

    async def start_workflow(self):

        # configurable params
        # demo_env = app_config.demo_env
        pudu_robot = app_config.environments["pudu_robot"]
        pudu_fleet = app_config.environments["pudu_fleet"]
        pudu_charger = app_config.environments["pudu_charger"]
        pudu_scm = app_config.environments["pudu_scm"]
        iso_bed = app_config.environments["iso_bed"]
        delivery_delay = app_config.delays["delivery"]

        # overwrite params
        self.robot_id = pudu_robot
        self.robot_fleet = pudu_fleet
        self.location = iso_bed

        adhoc_delivery_service = Rmf2Service(name="adhoc_delivery")

        pudu_scm_data = {
            "category": "go_to_place",
            "start": pudu_charger,
            "robot": self.robot_id,
            "fleet": self.robot_fleet,
        }

        send_scm_pudu = SequenceRoboticTask(
            name="send_pudu", serviceId=adhoc_delivery_service.id, data=pudu_scm_data
        )

        pudu_data = {
            "category": "zone",
            "start": self.location,
            "robot": self.robot_id,
            "fleet": self.robot_fleet,
            "zoneType": self.zone_type,
        }

        send_pudu = SequenceRoboticTask(
            name="send_pudu", serviceId=adhoc_delivery_service.id, data=pudu_data
        )

        send_pudu_arrive = SequenceNotification(
            name="send_pudu_arrive",
            serviceId=adhoc_delivery_service.id,
            userGroup=self.senderGroup,
            robotId=self.robot_id,
            location=self.location,
            other=self.items,
        )

        play_sound = SequencePuduTask(name="play_sound", delay=delivery_delay)

        pudu_return_data = {
            "category": "go_to_place",
            "start": pudu_scm,
            "robot": self.robot_id,
            "fleet": self.robot_fleet,
        }

        return_pudu = SequenceRoboticTask(
            name="return_pudu",
            serviceId=adhoc_delivery_service.id,
            data=pudu_return_data,
        )

        adhoc_delivery_service.tasks = [
            # send_scm_pudu,
            send_pudu,
            send_pudu_arrive,
            play_sound,
            return_pudu,
        ]

        try:
            asyncio.create_task(adhoc_delivery_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"adhoc_delivery_service workflow failed: {e}")

        return adhoc_delivery_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
