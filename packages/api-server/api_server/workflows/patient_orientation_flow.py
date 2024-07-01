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


class PatientOrientationFlow:
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
        # demo_env = app_config.demo_env
        temi_robot = app_config.environments["temi_robot"]
        temi_fleet = app_config.environments["temi_fleet"]
        temi_charger = app_config.environments["temi_charger"]
        iso_bed = app_config.environments["iso_bed"]
        temi_id = app_config.temi["temi_id"]

        patient_orientation_service = Rmf2Service(name="patient_orient")

        temi_data = {
            "category": "zone",
            "start": iso_bed,
            "robot": temi_robot,
            "fleet": temi_fleet,
            "zoneType": "human_facing",
        }
        send_temi = SequenceRoboticTask(
            name="send_temi", serviceId=patient_orientation_service.id, data=temi_data
        )

        temi_sequence = {
            "temi_id": temi_id,
            "sequence_type": "video",
        }

        play_video = SequenceTemiTask(name="play_video", data=temi_sequence)

        temi_return_data = {
            "category": "go_to_place",
            "start": temi_charger,
            "robot": temi_robot,
            "fleet": temi_fleet,
        }
        return_temi = SequenceRoboticTask(
            name="return_temi",
            serviceId=patient_orientation_service.id,
            data=temi_return_data,
        )

        patient_orientation_service.tasks = [send_temi, play_video, return_temi]
        try:
            asyncio.create_task(patient_orientation_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"aw patient exit workflow failed: {e}")

        return patient_orientation_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
