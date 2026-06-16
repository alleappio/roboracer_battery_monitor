from threading import Lock

class Telemetry:
    def __init__(self):
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
        
        self.stable_data = dict(self.data)
        self.lock = Lock()
    
    def update(self, value_name, value):
        self.data[value_name] = value
        with self.lock:
            self.received_value[value_name] = True
            all_received_flag = True
            for i in self.received_value:
                if self.received_value[i] == False:
                    all_received_flag = False

            if all_received_flag:
                for i in self.received_value:
                    self.received_value[i] = False
                    self.stable_data[i] = self.data[i]

    def read(self):
        with self.lock:
            snapshot = dict(self.stable_data)
        return snapshot
