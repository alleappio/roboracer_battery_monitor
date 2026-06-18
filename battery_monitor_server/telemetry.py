from threading import Lock
from collections import deque

class Telemetry:
    def __init__(self, window_size = 5, weight_old = 0.0, weight_new = 1.0):
        self.window_size = window_size
        self.weight_new = weight_new
        self.weight_old = weight_old
        self.received_value = {
            "voltage": False,
            "current": False,
            "rpm": False,
            "avgMotorCurrent": False,
            "ampHours": False,
            "wattHours": False,
            "tachometer": False,
            "tempMotor": False,
        }

        self.data = {
            "voltage": 0.0,
            "current": 0.0,
            "rpm": 0.0,
            "avgMotorCurrent": 0.0,
            "ampHours": 0.0,
            "wattHours": 0.0,
            "tachometer": 0.0,
            "tempMotor": 0.0,
        }
        
        self.history = {
            key: deque(maxlen=self.window_size) for key in self.data
        }
        self.smoothed_data = dict(self.data)
        self.stable_data = dict(self.data)
        self.stable_raw_data = dict(self.data)
        self.lock = Lock()
    
    def update(self, value_name, value):
        with self.lock:
            self.data[value_name] = value
            # self.history[value_name].append(value)

            # implement a moving average to smooth
            # self.smoothed_data[value_name] = sum(self.history[value_name]) / len(self.history[value_name])
            self.smoothed_data[value_name] = self.smoothed_data[value_name] * self.weight_old + self.data[value_name] * self.weight_new / (self.weight_old+self.weight_new)


            self.received_value[value_name] = True
            all_received_flag = all(self.received_value.values())

            if all_received_flag:
                for i in self.received_value:
                    self.received_value[i] = False
                    self.stable_raw_data[i] = self.data[i]
                    self.stable_data[i] = self.smoothed_data[i]

    def read(self):
        with self.lock:
            snapshot = dict(self.stable_data)
        return snapshot

    def read_raw(self):
        with self.lock:
            snapshot = dict(self.stable_raw_data)
        return snapshot
