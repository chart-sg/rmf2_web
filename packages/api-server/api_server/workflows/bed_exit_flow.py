import asyncio

from api_server.logger import logger
from api_server.rmf_io.rmf2_service import (
    Rmf2Service,
    SequenceCustom,
    SequenceNotification,
    SequenceRoboticTask,
)
from api_server.rmf_io.state_monitor import stateMonitor


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id: str, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class BedExitFlow:
    def __init__(self, body):
        self.service_id = body.service_id
        self.robot_id = body.data.robot_id
        self.data = {}

        # self.sm = stateMonitor()

    async def start_workflow(self):
        # Create task services
        responder_data = {
            "category": "teleop",
            "start": "iso",
            "robot": "temi",
            "fleet": "tinyRobot",
        }

        send_robot_responder_task = SequenceRoboticTask(
            name="send_robot_responder", data=responder_data
        )
        send_not = SequenceNotification(
            name="notify_ed",
            userId="iso_01",
            userGroup="iso_staff",
            message="Bed Exit triggered at Bed X",
            needAck=True,
            messageAction="telepresence",
        )
        send_robot_responder_task.next_task = send_not

        view_patient_task = SequenceCustom(name="view_patient")

        # send_aw_home= SequenceRoboticTask(name='send_aw_home', data=aw_data)
        # Send another robot after AW reach
        responder_return_data = {
            "category": "teleop",
            "start": "temi_charger",
            "robot": "temi",
            "fleet": "tinyRobot",
        }

        return_robot_task = SequenceRoboticTask(
            name="retun_robot_responder", data=responder_return_data
        )

        # TODO: if user choose telepresence, then perform next_task (view patient)
        # ELSE perform fail_task (return temi)
        send_not.next_task = view_patient_task
        send_not.fail_task = return_robot_task

        # return temi after video call ends
        view_patient_task.next_task = return_robot_task

        # Create a service
        bed_exit_service = Rmf2Service(name="bed_exit")

        try:
            # asyncio.create_task(send_aw_service.add_sequences_and_start(send_aw_task))
            await bed_exit_service.add_sequences_and_start(send_robot_responder_task)

        except RobotDispatchFailed as e:
            logger.error(f"bed exit workflow failed: {e}")


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
