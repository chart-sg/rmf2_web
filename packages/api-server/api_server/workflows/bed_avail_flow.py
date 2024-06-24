import asyncio

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


class BedAvailFlow:
    def __init__(self, body):

        self.data = body.data
        self.userId = body.requester
        self.patientId = body.data.patient_id
        self.senderGroup = body.requester_group
        self.receiverGroup = body.receiver_group

    async def start_workflow(self):

        # Create a service
        bed_avail_service = Rmf2Service(name="bed_avail")

        bed_avail_notif = SequenceNotification(
            serviceId=bed_avail_service.id,
            name="bed_avail_notif",
            location=self.data.location,
            userGroup=self.receiverGroup,
            patientId=self.patientId,
        )

        bed_avail_service.tasks = [bed_avail_notif]

        try:
            asyncio.create_task(bed_avail_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"bed avail service failed: {e}")

        return bed_avail_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
