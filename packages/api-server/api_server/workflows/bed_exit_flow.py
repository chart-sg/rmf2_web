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


class ZoneDirectionError(Exception):
    """Custom exception raised when a required attribute is missing."""


class BedExitFlow:
    def __init__(self, body):
        # self.service_id = body.service_id
        self.robot_id = body.data.robot_id
        self.data = {}

    async def start_workflow(self, data):
        try:
            # place = data["zone"]

            place = "bed_left" if data["direction"] == "left" else "bed_right"
            direction = data["direction"]
            angle = -45 if data["direction"] == "left" else -135
        except AttributeError:
            raise ZoneDirectionError("Missing required attribute(s) zone and direction")

        # configurable params
        # demo_env = app_config.demo_env
        temi_robot = app_config.environments["temi_robot"]
        temi_fleet = app_config.environments["temi_fleet"]
        temi_charger = app_config.environments["temi_charger"]
        temi_id = app_config.temi["temi_id"]

        bed_exit_service = Rmf2Service(name="bed_exit")

        responder_data = {
            "category": "go_to_place",
            "start": place,
            "robot": temi_robot,
            "fleet": temi_fleet,
            "zoneType": direction,
            "zoneFacing": angle,
        }

        send_robot_responder = SequenceRoboticTask(
            name="send_robot_responder",
            serviceId=bed_exit_service.id,
            data=responder_data,
        )

        temi_audio_data = {
            "temi_id": temi_id,
            "sequence_type": "pre_exit",
        }

        play_audio = SequenceTemiTask(name="play_audio", data=temi_audio_data)

        bed_exit_alert = SequenceNotification(
            name="bed_exit_alert",
            serviceId=bed_exit_service.id,
            robotId=temi_robot,
            location=place,
            userGroup="iso_nurse",
            messageAction="telepresence",
        )

        temi_sequence_data = {
            "temi_id": temi_id,
            "sequence_type": "bed_exit",
        }

        play_sequence = SequenceTemiTask(name="play_sequence", data=temi_sequence_data)

        temi_data = {"category": "teleop", "robot": temi_robot, "fleet": temi_fleet}
        manual_control = SequenceRoboticTask(
            name="send_temi", serviceId=bed_exit_service.id, data=temi_data
        )

        # bed_exit_service.tasks = [bed_exit_alert, [play_audio, send_robot_responder], play_sequence]
        # bed_exit_service.tasks = [bed_exit_alert, send_robot_responder, play_sequence]
        bed_exit_service.tasks = [bed_exit_alert]

        try:
            # await bed_exit_service.add_sequences_and_start(send_robot_responder)
            asyncio.create_task(bed_exit_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"bed exit workflow failed: {e}")

        return bed_exit_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
