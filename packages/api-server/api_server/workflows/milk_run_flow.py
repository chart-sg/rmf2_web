import asyncio

from api_server.app_config import app_config
from api_server.logger import logger
from api_server.rmf_io.rmf2_service_sequence import (
    Rmf2Service,
    SequenceCustom,
    SequenceMilkRun,
    SequenceNotification,
    SequenceRoboticTask,
)


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id: str, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class MilkRunFlow:
    def __init__(self, body=None):
        pass

    async def start_workflow(self, data=None):

        # specified slot to goto
        pudu_start = data["start"] if data is not None else None

        # configurable params
        demo_env = app_config.demo_env
        pudu_robot = app_config.environments["pudu_robot"]
        pudu_fleet = app_config.environments["pudu_fleet"]
        pudu_charger = app_config.environments["pudu_charger"]
        delay = app_config.delays["delivery"]

        # Create a service
        milk_run_service = Rmf2Service(name="pudu_milkrun")

        pudu_data = {
            "category": "zone",
            "start": pudu_start,
            "robot": pudu_robot,
            "fleet": pudu_fleet,
            "zoneType": "all",
            "delay": delay,
        }

        send_pudu_milk_run = SequenceMilkRun(
            name="send_pudu", data=pudu_data, serviceId=milk_run_service.id
        )

        milk_run_service.tasks = [send_pudu_milk_run]

        try:
            # asyncio.create_task(milk_run_service.start())
            await milk_run_service.start()
            # await send_aw_service.start()

        except RobotDispatchFailed as e:
            logger.error(f"milk_run service failed: {e}")

        return milk_run_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
