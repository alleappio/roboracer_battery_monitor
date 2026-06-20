#!/usr/bin/env python3

import csv

from mcap.reader import make_reader
from mcap_ros2.decoder import DecoderFactory

import sys


def main():

    try:
        mcap_file = sys.argv[1]
        output_csv = sys.argv[2]
        topic_name = sys.argv[3]
    except IndexError:
        print(f"usage: {sys.argv[0]} mcap_file output_csv topic_name")
        exit()

    with open(mcap_file, "rb") as f:

        reader = make_reader(
            f,
            decoder_factories=[DecoderFactory()]
        )

        with open(output_csv, "w", newline="") as csvfile:
            first = True
            for schema, channel, message, ros_msg in reader.iter_decoded_messages(
                topics=[topic_name]
            ):
                data = {
                    "current_motor": ros_msg.state.current_motor,
                    "current_input": ros_msg.state.current_input,
                    "avg_id": ros_msg.state.avg_id,
                    "avg_iq": ros_msg.state.avg_iq,
                    "duty_cycle": ros_msg.state.duty_cycle,
                    "speed": ros_msg.state.speed,
                    "voltage_input": ros_msg.state.voltage_input,
                    "charge_drawn": ros_msg.state.charge_drawn,
                    "charge_regen": ros_msg.state.charge_regen,
                    "energy_drawn": ros_msg.state.energy_drawn,
                    "energy_regen": ros_msg.state.energy_regen,
                    "displacement": ros_msg.state.displacement,
                    "distance_traveled": ros_msg.state.distance_traveled,
                    "fault_code": ros_msg.state.fault_code,
                    "pid_pos_now": ros_msg.state.pid_pos_now,
                    "controller_id": ros_msg.state.controller_id,
                    "avg_vd": ros_msg.state.avg_vd,
                    "avg_vq": ros_msg.state.avg_vq,
                }
                writer = csv.writer(csvfile)
                if first:
                    writer.writerow(data.keys())
                    first = False
                writer.writerow(data[i] for i in data)

    print(f"CSV written to: {output_csv}")


if __name__ == "__main__":
    main()
