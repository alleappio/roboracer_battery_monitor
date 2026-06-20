from threading import Lock
from collections import deque
import time

class Telemetry:
    def __init__(self, window_size = 5, new_measure_weight = 0.8, nominal_battery_amps = 5.0, nominal_battery_volts = 11.1):
        self.window_size = window_size
        self.weight_new = new_measure_weight
        self.weight_old = 1 - new_measure_weight
        self.nominal_battery_amps = nominal_battery_amps
        self.nominal_battery_volts = nominal_battery_volts
        self.received_value = {
            "dutyCycleNow": False,
            "wattHoursCharged": False,
            "tachometerAbs": False,
            "tempMosfet": False,
            "pidPos": False,
            "id": False,
            "error": False,
            "voltage": False,
            "current": False,
            "rpm": False,
            "avgMotorCurrent": False,
            "ampHours": False,
            "ampHoursCharged": False,
            "wattHours": False,
            "tachometer": False,
            "tempMotor": False,
        }

        self.data = {
            "dutyCycleNow": 0.0,
            "wattHoursCharged": 0.0,
            "tachometerAbs": 0.0,
            "tempMosfet": 0.0,
            "pidPos": 0.0,
            "id": 0.0,
            "error": 0.0,
            "voltage": 0.0,
            "current": 0.0,
            "rpm": 0.0,
            "avgMotorCurrent": 0.0,
            "ampHours": 0.0,
            "ampHoursCharged": 0.0,
            "wattHours": 0.0,
            "tachometer": 0.0,
            "tempMotor": 0.0,
            "estimateTempMotor": 0.0,
        }
        
        self.history = {
            key: deque(maxlen=self.window_size) for key in self.data
        }
        self.smoothed_data = dict(self.data)
        self.stable_data = dict(self.data)
        self.stable_data["measure_time"] = time.time()
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
                    self.stable_data["remainingCapacity"] = self.get_remaining_capacity()
                    self.stable_data["remainingTime"] = self.get_remaining_time()
                    self.stable_data["estimateTempMotor"] = self.get_motor_temperature()
                    self.stable_data["measure_time"] = time.time()

    def get_remaining_capacity(self):
        juice_left = self.nominal_battery_amps - (self.stable_data["ampHours"] - self.stable_data["ampHoursCharged"])
        return juice_left

    def get_remaining_time(self):
        time_left_in_hours = self.stable_data["remainingCapacity"]/max(self.stable_data["current"], 0.0000000000001)
        time_left_in_minutes = time_left_in_hours/60
        return time_left_in_minutes

    def get_motor_temperature(self):
        r_phase = 0.008       # Internal copper resistance (~8 mOhms)
        c_thermal = 180.0     # Scaled for a 262g metal mass motor
        h_0 = 0.08            # Stationary thermal dissipation factor
        h_1 = 0.00003         # Air dissipation factor (scales up linearly toward 50k RPM)
        t_ambient = 25        # °C
        delta_t = time.time() - self.stable_data["measure_time"]
        heat_in = self.stable_data["avgMotorCurrent"]**2 *r_phase
        cooling_factor = h_0 + (h_1 * self.stable_data["rpm"])
        heat_out = (self.stable_data["estimateTempMotor"] - t_ambient) * cooling_factor
        delta_temp = ((heat_in - heat_out) / c_thermal) * delta_t
        return self.stable_data["estimateTempMotor"] + delta_temp

    def read(self):
        with self.lock:
            snapshot = dict(self.stable_data)
        return snapshot

    def read_raw(self):
        with self.lock:
            snapshot = dict(self.stable_raw_data)
        return snapshot
