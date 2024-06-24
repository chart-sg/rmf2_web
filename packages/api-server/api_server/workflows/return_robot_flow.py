import asyncio

from api_server.logger import logger
from api_server.rmf_io.rmf2_service_sequence import (
    Rmf2Service,
    SequenceNotification,
    SequenceRoboticTask,
)
from api_server.rmf_io.state_monitor import stateMonitor


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class ReturnRobotFlow:
    def __init__(self, body):

        self.robot_id = body.data.robot_id
        self.location = body.data.location
        self.robot_fleet = (
            body.data.robot_fleet if body.data.robot_fleet is not None else "tinyRobot"
        )

        self.data = body.data
        self.userId = body.requester
        self.userGroup = body.requester_group

    async def start_workflow(self):
        return_robot_service = Rmf2Service(name="return_robot")

        robot_data = {
            "category": "go_to_place",
            "start": self.location,
            "robot": self.robot_id,
            "fleet": self.robot_fleet,
        }

        return_robot = SequenceRoboticTask(
            name="return_robot", serviceId=return_robot_service.id, data=robot_data
        )
        return_robot_service.tasks = [return_robot]

        try:
            asyncio.create_task(return_robot_service.start())
            # await send_aw_service.add_sequences_and_start(return_temi)

        except RobotDispatchFailed as e:
            logger.error(f"send aw service failed: {e}")

        return return_robot_service.id


def main():
    workflow = ReturnRobotFlow()
    asyncio.run(workflow.start_workflow())


if __name__ == "__main__":
    main()
