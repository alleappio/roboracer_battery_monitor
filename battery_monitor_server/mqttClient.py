import paho.mqtt.client as mqtt
from telemetry import Telemetry

class MqttClient:
    last_message = {}
    received_value = {}
    def __init__(self, ip, port, id, wildcard, telemetry):
        self.telemetry = telemetry

        self.ip = ip
        self.port = port
        self.id = id
        self.wildcard = wildcard

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.ip, self.port, 60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code:", rc)
        client.subscribe(self.wildcard)
        print(f"subscribed to topic: {self.wildcard}")

    def on_message(self, client, userdata, msg):
        self.process_message(msg.topic, msg.payload.decode())

    def process_message(self, topic, message):
        splitted = topic.split("/")
        value_name = splitted[-1]
        self.last_message[value_name] = message
        self.telemetry.update(value_name, float(message))

    def get_last_message(self, value_name):
        return self.last_message.get(value_name, None)
