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


class AwPatientExitFlow:
    def __init__(self, body):

        self.robot_id = body.data.robot_id
        self.location = body.data.location
        self.robot_fleet = (
            body.data.robot_fleet if body.data.robot_fleet is not None else None
        )
        self.zone_type = (
            [body.data.zone_type] if body.data.zone_type is not None else "all"
        )

        self.data = body.data
        self.userId = body.requester
        self.patientId = body.data.patient_id
        self.senderGroup = body.requester_group
        self.receiverGroup = body.receiver_group

    async def start_workflow(self):

        # configurable params
        demo_env = app_config.demo_env
        aw_robot = app_config.environments[demo_env]["aw_robot"]
        aw_fleet = app_config.environments[demo_env]["aw_fleet"]

        aw_patient_exit_service = Rmf2Service(name="temi_orient")

        aw_disinfect_data = {
            "category": "zone",
            "start": "disinfection",
            "robot": aw_robot,
            "fleet": aw_fleet,
            "zoneType": "all",
        }

        send_aw_disinfect = SequenceRoboticTask(
            name="send_aw_disinfect",
            serviceId=aw_patient_exit_service.id,
            data=aw_disinfect_data,
        )

        aw_patient_exit_service.tasks = [send_aw_disinfect]
        try:
            asyncio.create_task(aw_patient_exit_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"aw patient exit workflow failed: {e}")

        return aw_patient_exit_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
