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


class ViewPatientFlow:
    def __init__(self, body):
        # self.sm = stateMonitor()
        # self.service_id = body.service_name
        self.robot_id = body.data.robot_id
        self.location = body.data.location

        # self.robot_fleet = body.data.robot_fleet
        self.robot_fleet = "tinyRobot"

        self.zone_type = (
            [body.data.zone_type] if body.data.zone_type is not None else "all"
        )
        # self.zone_type = ["all"]

        self.data = body.data
        self.userId = body.requester
        self.senderGroup = body.requester_group
        self.receiverGroup = body.receiver_group

    async def start_workflow(self):

        # Create a service
        view_patient_service = Rmf2Service(name="send_aw")

        aw_data = {
            "category": "zone",
            "start": self.data.location,
            "robot": self.robot_id,
            "fleet": self.robot_fleet,
            "zoneType": self.zone_type,
        }

        send_aw = SequenceRoboticTask(
            name="view_patient", serviceId=view_patient_service.id, data=aw_data
        )

        temi_data = {
            "temi_id": "00121285864",
            "sequence_type": "call",
        }
        play_video = SequenceTemiTask(name="play_video", data=temi_data)

        view_patient_service.tasks = [play_video]

        try:
            asyncio.create_task(view_patient_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"view patient service failed: {e}")

        return view_patient_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
