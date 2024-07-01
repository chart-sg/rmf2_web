import asyncio

from api_server.app_config import app_config
from api_server.logger import logger
from api_server.rmf_io.rmf2_service_sequence import (
    Rmf2Service,
    SequenceMilkRun,
    SequenceNotification,
    SequenceRoboticTask,
)


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id: str, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class SendFFFlow:
    def __init__(self, body):
        # self.sm = stateMonitor()
        self.robot_id = body.data.robot_id
        self.location = body.data.location

        self.zone_type = (
            [body.data.zone_type] if body.data.zone_type is not None else "all"
        )
        self.zone_facing = (
            body.data.zone_facing if body.data.zone_facing is not None else None
        )

        self.data = body.data
        self.userId = body.requester
        self.patientId = body.data.patient_id
        self.senderGroup = body.requester_group
        self.receiverGroup = body.receiver_group

    async def start_workflow(self):

        # configurable params
        # demo_env = app_config.demo_env
        aw_robot = app_config.environments["aw_robot"]
        aw_fleet = app_config.environments["aw_fleet"]
        delay = app_config.delays["delivery"]

        # overwrite params
        self.robot_id = aw_robot
        self.robot_fleet = aw_fleet

        # Create a service
        send_ff_service = Rmf2Service(name="send_aw")

        aw_data = {
            "category": "zone",
            "start": self.data.location,
            "robot": self.robot_id,
            "fleet": self.robot_fleet,
            "zoneType": self.zone_type,
            "zoneFacing": 180,
        }

        send_aw = SequenceRoboticTask(
            name="send_aw", serviceId=send_ff_service.id, data=aw_data
        )

        schedule_doctor_consult = SequenceNotification(
            serviceId=send_ff_service.id,
            name="schedule_doctor_consult",
            robotId=self.robot_id,
            location=self.data.location,
            userGroup="ed_doctor",
            patientId=self.patientId,
        )

        send_aw_receiver = SequenceNotification(
            serviceId=send_ff_service.id,
            name="send_aw_receiver",
            robotId=self.robot_id,
            location=self.data.location,
            userGroup=self.receiverGroup,
            patientId=self.patientId,
        )

        send_ff_service.tasks = [send_aw, [schedule_doctor_consult, send_aw_receiver]]

        try:
            asyncio.create_task(send_ff_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"send ff service failed: {e}")

        return send_ff_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
