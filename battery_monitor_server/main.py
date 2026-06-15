import paho.mqtt.client as mqtt
import json
from parameters import *

last_message = {}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code:", rc)
    client.subscribe(MQTT_WILDCARD_TOPIC)
    print(f"subscribed to topic: {MQTT_WILDCARD_TOPIC}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"{msg.topic}: {payload}")
    last_message[msg.topic] = payload

def main() -> None:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_IP, BROKER_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()
