from PyQt6.QtWidgets import QApplication
import paho.mqtt.client as mqtt
import json
from parameters import *
from mqttClient import MqttClient
from dashboard import Dashboard
import sys

def main() -> None:
    # mqtt_client = mqttClient(BROKER_IP, BROKER_PORT, MQTT_ID, MQTT_WILDCARD_TOPIC)
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
