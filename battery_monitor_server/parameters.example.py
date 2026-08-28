import os


BROKER_IP = os.getenv("BROKER_IP", "localhost")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))

MQTT_ID = os.getenv("MQTT_ID", "server")
MQTT_WILDCARD_TOPIC = os.getenv("MQTT_WILDCARD_TOPIC", "foobar/#")

NEW_MEASURE_WEIGHT = float(os.getenv("NEW_MEASURE_WEIGHT", "0.5"))

NOMINAL_BATTERY_AMPS = float(os.getenv("NOMINAL_BATTERY_AMPS", "5.0"))
NOMINAL_BATTERY_VOLTAGE = float(os.getenv("NOMINAL_BATTERY_VOLTAGE", "11.1"))
MAXIMUM_BATTERY_VOLTAGE = float(os.getenv("MAXIMUM_BATTERY_VOLTAGE", "12.6"))
