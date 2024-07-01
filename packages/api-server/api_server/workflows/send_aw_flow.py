import asyncio

from api_server.app_config import app_config
from api_server.logger import logger
from api_server.rmf_io.rmf2_service_sequence import (
    Rmf2Service,
    SequenceNotification,
    SequenceRoboticTask,
)
from api_server.rmf_io.state_monitor import stateMonitor


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id: str, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class SendAWFlow:
    def __init__(self, body):
        self.sm = stateMonitor()
        # self.service_id = body.service_name
        self.robot_id = body.data.robot_id
        self.location = body.data.location

        self.robot_fleet = (
            body.data.robot_fleet if body.data.robot_fleet is not None else "tinyRobot"
        )
        # self.robot_fleet = "tinyRobot"

        self.zone_type = (
            [body.data.zone_type] if body.data.zone_type is not None else "all"
        )
        self.zone_facing = (
            body.data.zone_facing if body.data.zone_facing is not None else None
        )
        # self.zone_type = ["all"]

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

        # overwrite params
        # self.robot_id = aw_robot
        self.robot_fleet = aw_fleet

        # Create a service
        send_aw_service = Rmf2Service(name="send_aw")

        # AP1 workaround : set orient to 180 if going to FF
        if self.data.location == "ff":
            self.zone_facing = 180

        aw_data = {
            "category": "zone",
            "start": self.data.location,
            "robot": self.robot_id,
            "fleet": self.robot_fleet,
            "zoneType": self.zone_type,
            "zoneFacing": self.zone_facing,
        }

        send_aw = SequenceRoboticTask(
            name="send_aw", serviceId=send_aw_service.id, data=aw_data
        )

        send_aw_sender = SequenceNotification(
            serviceId=send_aw_service.id,
            name="send_aw_sender",
            robotId=self.robot_id,
            location=self.data.location,
            userGroup=self.senderGroup,
            patientId=self.patientId,
        )

        send_aw_receiver = SequenceNotification(
            serviceId=send_aw_service.id,
            name="send_aw_receiver",
            robotId=self.robot_id,
            location=self.data.location,
            userGroup=self.receiverGroup,
            patientId=self.patientId,
        )

        send_aw_service.tasks = [send_aw, [send_aw_sender, send_aw_receiver]]

        try:
            asyncio.create_task(send_aw_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"send aw service failed: {e}")

        return send_aw_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
