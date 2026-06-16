from PyQt6.QtWidgets import QApplication
import json
from parameters import *
from mqttClient import MqttClient
from dashboard.dashboard import Dashboard
import sys
import uvicorn
from fastapi import FastAPI
import threading
from telemetry import Telemetry

def run_webapp(app):
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main() -> None:
    telemetry = Telemetry()
    dashboard = Dashboard(telemetry)
    threading.Thread(target = run_webapp, args = (dashboard.app,), daemon = True).start()
    mqtt_client = MqttClient(BROKER_IP, BROKER_PORT, MQTT_ID, MQTT_WILDCARD_TOPIC, telemetry)


if __name__ == '__main__':
    main()
