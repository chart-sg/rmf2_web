import asyncio

from api_server.logger import logger
from api_server.rmf_io.rmf2_service import (
    Rmf2Service,
    SequenceNotification,
    SequenceRoboticTask,
)
from api_server.rmf_io.state_monitor import stateMonitor

# from api_server.models import (
#     DoorState,
#     DispenserState,
#     IngestorState,
#     FleetState,
#     TaskState,
#     LiftState,
# )


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id: str, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class TestFlow:
    def __init__(self, body):
        self.service_id = body.service_id
        self.robot_id = body.data.robot_id
        self.data = {}

        self.sm = stateMonitor()
        # self.gw = rmf_gateway()

    def get_pos_from_aw(self):
        # retrieve AW's parking slot
        current = self.sm.get_robot_position(robot="aw", fleet="tinyRobot")

        # Coordinates for ff_zone_c
        target_x = 13.472711563110352
        target_y = -9.051843643188477
        target = [target_x, target_y]

        # logic to tell AW partner where to go
        if self.sm.pos_checker(current, target):
            position = "ff_zone_right"
        else:
            position = "ff_zone_left"

        # position = "ff_zone_right"
        logger.info(f"Get partner to go to: {position}")
        return position

    async def start_workflow(self):
        # Create task services
        aw_data = {
            "category": "teleop",
            "start": "ff_zone_c",
            "robot": self.robot_id,
            "fleet": "tinyRobot",
        }

        send_aw_task = SequenceRoboticTask(name="send_aw_ff", data=aw_data)
        notify_aw_ed = SequenceNotification(
            name="notify_ed",
            userId="ed_01",
            userGroup="ed_staff",
            message="AW has reached ED STK",
            needAck=True,
        )
        send_aw_task.next_task = notify_aw_ed

        # send_aw_home= SequenceRoboticTask(name='send_aw_home', data=aw_data)

        # Send another robot after AW reach
        pudu_data = {
            "category": "teleop",
            "start": self.get_pos_from_aw,  # depend on AW location
            "robot": "pudu",
            "fleet": "tinyRobot",
        }
        send_pudu_task = SequenceRoboticTask(name="send_pudu", data=pudu_data)
        notify_aw_ed.next_task = send_pudu_task
        # send_aw_task.next_task = [notify_aw_ed,send_pudu_task]

        # notify_pudu_ed = SequenceNotification(name='notify_ed',userId="ed_01",userGroup="ed_staff" ,message="PUDU has reached ED STK",messageWithAction="ok")
        # send_pudu_task.next_task = notify_pudu_ed

        # Create correction task services
        # aw_fail_data = {
        #     "category":"teleop",
        #     "start":"concierge",
        #     "robot":"aw",
        #     "fleet":"tinyRobot"
        # }

        # aw_return_task = SequenceRoboticTask(name='return_aw_fail', data=aw_fail_data)
        # notify_aw_fail = SequenceNotification(name='notify_ed_fail',userId="ed_01",userGroup="ed_staff" ,message="AW failed to reach ED STK, returning to concierge",messageWithAction="ok")
        # aw_fail_task = [aw_return_task,notify_aw_fail]
        # send_aw_task.fail_task = aw_fail_task

        # Create a service
        send_aw_service = Rmf2Service(name="send_aw")

        try:
            # asyncio.create_task(send_aw_service.add_sequences_and_start(send_aw_task))
            await send_aw_service.add_sequences_and_start(send_aw_task)

        except RobotDispatchFailed as e:
            logger.error(f"admit to ff workflow failed: {e}")


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
