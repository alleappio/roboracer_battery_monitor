import paho.mqtt.client as mqtt
import time
import random

# ======================
# CONFIG
# ======================
BROKER = "192.168.1.102"
PORT = 1883
MQTT_ID = "squeaky"

# ======================
# CLIENT
# ======================
client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# ======================
# FIELDS (come nel tuo ESP32)
# ======================
fields = [
    "dutyCycleNow",
    "wattHoursCharged",
    "tachometerAbs",
    "tempMosfet",
    "pidPos",
    "id",
    "error",
    "voltage",
    "current",
    "rpm",
    "avgMotorCurrent",
    "ampHours",
    "ampHoursCharged",
    "wattHours",
    "tachometer",
    "tempMotor",
]

# ======================
# SIMULATION LOOP
# ======================
while True:

    for field in fields:

        # fake realistic ranges
        if field == "voltage":
            value = random.uniform(20.0, 25.0)
        elif field == "current":
            value = random.uniform(0.0, 10.0)
        elif field == "rpm":
            value = random.randint(0, 5000)
        elif field == "tempMotor":
            value = random.uniform(25.0, 80.0)
        else:
            value = random.uniform(0.0, 100.0)

        topic = f"{MQTT_ID}/{field}"
        message = f"{value:.2f}"

        client.publish(topic, message)

        print(f"{topic}: {message}")

    time.sleep(1)
