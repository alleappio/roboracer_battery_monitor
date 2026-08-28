#!/usr/bin/env python3

import argparse
import csv
import time

import paho.mqtt.client as mqtt


DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 1883
DEFAULT_MQTT_ID = "squeaky"
DEFAULT_RATE = 20 # hz

# CSV column -> MQTT telemetry field
CSV_MAP = {
    "current_motor": "avgMotorCurrent",
    "current_input": "current",
    "duty_cycle": "dutyCycleNow",
    "speed": "rpm",
    "voltage_input": "voltage",
    "charge_drawn": "ampHours",
    "charge_regen": "ampHoursCharged",
    "energy_drawn": "wattHours",
    "energy_regen": "wattHoursCharged",
    "displacement": "tachometer",
    "distance_traveled": "tachometerAbs",
    "pid_pos_now": "pidPos",
    "controller_id": "id",
    "fault_code": "error",
}

# Fields required by the server but not present in the CSV
DEFAULT_VALUES = {
    "tempMosfet": 30.0,
    "tempMotor": 30.0,
}


def publish_row(client, mqtt_id, row, last_tachometer_abs):
    payload = dict(DEFAULT_VALUES)

    for csv_key, mqtt_key in CSV_MAP.items():
        if csv_key not in row or row[csv_key] == "":
            continue
        payload[mqtt_key] = row[csv_key]

    # Keep types sane for the server
    payload["voltage"] = float(payload["voltage"])
    payload["current"] = float(payload["current"])
    payload["rpm"] = float(payload["rpm"])
    payload["avgMotorCurrent"] = float(payload["avgMotorCurrent"])
    payload["dutyCycleNow"] = float(payload["dutyCycleNow"])
    payload["ampHours"] = float(payload["ampHours"])
    payload["ampHoursCharged"] = float(payload["ampHoursCharged"])
    payload["wattHours"] = float(payload["wattHours"])
    payload["wattHoursCharged"] = float(payload["wattHoursCharged"])
    payload["pidPos"] = float(payload["pidPos"])
    payload["id"] = int(float(payload["id"]))
    payload["error"] = int(float(payload["error"]))

    # If the CSV value is missing or non-monotonic, keep the counter stable
    try:
        tach_abs = int(float(payload["tachometerAbs"]))
        last_tachometer_abs = max(last_tachometer_abs, tach_abs)
    except Exception:
        pass
    payload["tachometerAbs"] = last_tachometer_abs
    payload["tachometer"] = int(float(payload["tachometer"]))

    for field, value in payload.items():
        client.publish(f"{mqtt_id}/{field}", str(value))

    return last_tachometer_abs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("--broker", default=DEFAULT_BROKER)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--mqtt-id", default=DEFAULT_MQTT_ID)
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE, help="rows per second")
    parser.add_argument("--loop", action="store_true", help="restart at end of file")
    args = parser.parse_args()

    period = 1.0 / args.rate

    client = mqtt.Client()
    client.connect(args.broker, args.port, 60)
    client.loop_start()

    print(f"Streaming {args.csv_file} at {args.rate:.2f} Hz")

    last_tachometer_abs = 0

    while True:
        with open(args.csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                start = time.monotonic()
                last_tachometer_abs = publish_row(
                    client, args.mqtt_id, row, last_tachometer_abs
                )
                elapsed = time.monotonic() - start
                time.sleep(max(0.0, period - elapsed))

        if not args.loop:
            break

    client.loop_stop()
    client.disconnect()
    print("Done")


if __name__ == "__main__":
    main()
