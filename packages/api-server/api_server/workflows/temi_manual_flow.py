import asyncio

from api_server.app_config import app_config
from api_server.logger import logger
from api_server.rmf_io.rmf2_service_sequence import (
    Rmf2Service,
    SequenceCustom,
    SequenceNotification,
    SequenceRoboticTask,
    SequenceTemiTask,
)


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id: str, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class TemiManualFlow:
    def __init__(self, body):

        self.robot_id = body.data.robot_id
        self.location = body.data.location
        self.robot_fleet = (
            body.data.robot_fleet if body.data.robot_fleet is not None else None
        )

        self.data = body.data
        self.userId = body.requester
        self.patientId = body.data.patient_id
        self.senderGroup = body.requester_group
        self.receiverGroup = body.receiver_group

    async def start_workflow(self):

        # configurable params
        demo_env = app_config.demo_env
        temi_robot = app_config.environments[demo_env]["temi_robot"]
        temi_fleet = app_config.environments[demo_env]["temi_fleet"]
        iso_bed = app_config.environments[demo_env]["iso_bed"]
        temi_charger = app_config.environments[demo_env]["temi_charger"]
        temi_id = app_config.temi["temi_id"]

        temi_manual_service = Rmf2Service(name="patient_orient")

        temi_data = {
            "category": "teleop",
            "start": iso_bed,
            "robot": temi_robot,
            "fleet": temi_fleet,
        }
        manual_control = SequenceRoboticTask(
            name="send_temi", serviceId=temi_manual_service.id, data=temi_data
        )

        temi_manual_service.tasks = [manual_control]
        try:
            asyncio.create_task(temi_manual_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"manual workflow failed: {e}")

        return temi_manual_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
