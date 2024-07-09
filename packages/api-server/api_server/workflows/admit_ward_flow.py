import asyncio

from api_server.app_config import app_config
from api_server.logger import logger
from api_server.rmf_io.rmf2_service_sequence import (
    Rmf2Service,
    SequenceApiCall,
    SequenceCustom,
    SequenceNotification,
    SequenceRoboticTask,
)


class RobotDispatchFailed(Exception):
    def __init__(self, robot_id: str, message="Dispatch failed"):
        self.robot_id = robot_id
        self.message = f"Robot {self.robot_id}: {message}"
        super().__init__(self.message)


class AdmitWardFlow:
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
        # demo_env = app_config.demo_env
        aw_robot = app_config.environments["aw_robot"]
        aw_fleet = app_config.environments["aw_fleet"]
        iso_bed = app_config.environments["aw_bed"]
        trigger_url = app_config.aw["check_aw_exit"]

        # overwrite params
        self.robot_fleet = aw_fleet
        self.robot_id = aw_robot
        self.location = iso_bed

        admit_ward_service = Rmf2Service(name="admit_ward")

        # AP1 workaround : go to lift zone in order to enter lift
        # aw_lift_data = {
        #     "category": "zone",
        #     "start": "lift_waiting",
        #     "robot": self.robot_id,
        #     "fleet": self.robot_fleet,
        #     "zoneType": "all",
        # }

        # send_aw_lift = SequenceRoboticTask(
        #     name="send_aw", serviceId=admit_ward_service.id, data=aw_lift_data
        # )

        # AP1 workaround : go to door 1 before entering bed zone
        aw_door_data = {
            "category": "go_to_place",
            "start": "door_1",
            "robot": self.robot_id,
            "fleet": self.robot_fleet,
        }

        send_aw_door = SequenceRoboticTask(
            name="send_aw", serviceId=admit_ward_service.id, data=aw_door_data
        )

        aw_data = {
            "category": "zone",
            "start": "ward",
            "robot": self.robot_id,
            "fleet": self.robot_fleet,
            "zoneType": "all",
        }

        send_aw = SequenceRoboticTask(
            name="send_aw", serviceId=admit_ward_service.id, data=aw_data
        )

        notify_aw_receiver = SequenceNotification(
            name="admit_ward_receiver",
            serviceId=admit_ward_service.id,
            robotId=self.robot_id,
            location=self.data.location,
            userGroup=self.receiverGroup,
            patientId=self.patientId,
        )

        trigger_data = {"url": trigger_url, "method": "GET"}

        trigger_aw_check = SequenceApiCall(name="trigger_aw_check", data=trigger_data)

        admit_ward_service.tasks = [
            # send_aw_lift,
            send_aw_door,
            send_aw,
            notify_aw_receiver,
            trigger_aw_check,
        ]
        try:
            asyncio.create_task(admit_ward_service.start())

        except RobotDispatchFailed as e:
            logger.error(f"admit ward workflow failed: {e}")

        return admit_ward_service.id


def main():
    pass


if __name__ == "__main__":
    # main()
    pass
