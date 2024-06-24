# mqtt_client.py
from typing import Callable, Dict, Optional

import paho.mqtt.client as mqtt


class MqttClient:
    def __init__(
        self, broker="mqtt.eclipse.org", port=1883, username=None, password=None
    ):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port

        if username and password:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {str(rc)}")

    def on_message(self, client, userdata, msg):
        print(f"{msg.topic} {str(msg.payload)}")

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def publish(self, topic, message):
        self.client.publish(topic, message)


_mqtt_client: Optional[MqttClient] = None


def mqtt_client() -> MqttClient:
    return _mqtt_client


def pudu_client() -> MqttClient:
    return _pudu_mqtt_client


def startup():
    """
    Starts subscribing to all MQTT topic.
    """
    global _mqtt_client, _pudu_mqtt_client
    _mqtt_client = MqttClient(
        broker="10.233.0.80", port=1883, username="chart", password="chartmqtt"
    )
    _pudu_mqtt_client = MqttClient(
        broker="10.0.0.13", port=1883, username="status_sc", password="BLANKi12345"
    )

    _mqtt_client.start()
    _pudu_mqtt_client.start()

    return _mqtt_client
