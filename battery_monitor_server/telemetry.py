from threading import Lock
from collections import deque
import time

class Telemetry:
    def __init__(self, window_size = 5, new_measure_weight = 0.8, nominal_battery_amps = 5.0, nominal_battery_volts = 11.1, battery_max_voltage = 12.6):
        self.window_size = window_size
        self.weight_new = new_measure_weight
        self.weight_old = 1 - new_measure_weight
        self.nominal_battery_amps = nominal_battery_amps
        self.nominal_battery_volts = nominal_battery_volts
        self.battery_max_voltage = battery_max_voltage
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
            "remainingTime": 0.0,
            "stateOfCharge": 50.0
        }
        
        self.history = {
            key: deque(maxlen=self.window_size) for key in self.data
        }
        self.smoothed_data = dict(self.data)
        self.stable_data = dict(self.data)
        self.stable_data["measureTime"] = time.time()
        self.stable_raw_data = dict(self.data)
        self.lock = Lock()
    
    def update(self, value_name, value):
        with self.lock:
            self.data[value_name] = value
            self.history[value_name].append(value)

            # implement a moving average to smooth
            # self.smoothed_data[value_name] = sum(self.history[value_name]) / len(self.history[value_name])
            self.smoothed_data[value_name] = self.smoothed_data[value_name] * self.weight_old + self.data[value_name] * self.weight_new

            self.received_value[value_name] = True
            all_received_flag = all(self.received_value.values())

            if all_received_flag:
                for i in self.received_value:
                    self.received_value[i] = False
                    self.stable_raw_data[i] = self.data[i]
                    self.stable_data[i] = self.smoothed_data[i]
                
                # calculate interesting data
                self.stable_data["remainingCapacity"] = self.get_remaining_capacity() # A/h
                self.stable_data["remainingTime"] = self.get_remaining_time() # seconds
                self.stable_data["estimateTempMotor"] = self.get_motor_temperature() # °C
                self.stable_data["stateOfCharge"] = self.get_state_of_charge() # %
                self.stable_data["lowPowerAlert"] = self.get_low_power_alert()
                # print(f"delta t = {(time.time() - self.stable_data["measureTime"])*1000} ms")
                self.stable_data["measureTime"] = time.time()

    def get_remaining_capacity(self):
        used_ah = self.stable_data["ampHours"] - self.stable_data["ampHoursCharged"]
        juice_left = self.nominal_battery_amps - used_ah
        return juice_left

    def get_remaining_time(self):
        if(self.stable_data["current"]<0.05):
            return self.stable_data["remainingTime"]
        time_left_in_hours = self.stable_data["remainingCapacity"]/max(self.stable_data["current"], 0.05)
        time_left_in_seconds = self.stable_data["remainingTime"]*self.weight_old + (time_left_in_hours*60*60)*self.weight_new
        return time_left_in_seconds

    def get_motor_temperature(self):
        r_phase = 0.008       # Internal copper resistance (~8 mOhms)
        c_thermal = 180.0     # Scaled for a 262g metal mass motor
        h_0 = 0.08            # Stationary thermal dissipation factor
        h_1 = 0.00003         # Air dissipation factor (scales up linearly toward 50k RPM)
        t_ambient = 25        # °C
        delta_t = time.time() - self.stable_data["measureTime"]
        heat_in = self.stable_data["avgMotorCurrent"]**2 *r_phase
        cooling_factor = h_0 + (h_1 * self.stable_data["rpm"])
        heat_out = (self.stable_data["estimateTempMotor"] - t_ambient) * cooling_factor
        delta_temp = ((heat_in - heat_out) / c_thermal) * delta_t
        return self.stable_data["estimateTempMotor"] + delta_temp

    def get_state_of_charge(self):
    # def update_state_of_charge(self, voltage=None, current=None, timestamp=None):
        now = time.time()
        dt_hours = max(0.0, now - getattr(self, "last_soc_update_time", self.stable_data["measureTime"])) / 3600.0

        if dt_hours > 0 and self.stable_data["current"] is not None and self.nominal_battery_amps > 0:
            # Assumes positive current = discharge, negative current = charge.
            delta_soc = (self.stable_data["current"] * dt_hours / self.nominal_battery_amps) * 100.0
            self.stable_data["stateOfCharge"] -= delta_soc

        # Use voltage correction only when the pack is close to idle.
        if self.stable_data["voltage"] is not None and self.stable_data["current"] is not None and abs(self.stable_data["current"]) <= 0.5:
            voltage_soc = self._soc_from_voltage(self.stable_data["voltage"])
            self.stable_data["stateOfCharge"] = (self.weight_old * self.stable_data["stateOfCharge"]) + (self.weight_new * voltage_soc)

            # If the pack is clearly full, snap to 100%.
            if voltage_soc >= 98.0:
                self.stable_data["stateOfCharge"] = 100.0

        self.stable_data["stateOfCharge"] = max(0.0, min(100.0, self.stable_data["stateOfCharge"]))
        self.last_soc_update_time = now
        return self.stable_data["stateOfCharge"]

    def _soc_from_voltage(self, voltage):
        if voltage is None:
            return 0.0

        try:
            voltage = float(voltage)
        except (TypeError, ValueError):
            return 0.0

        v_min = float(self.nominal_battery_volts)
        v_max = float(self.battery_max_voltage)

        if v_max <= v_min:
            return 0.0

        soc = (voltage - v_min) / (v_max - v_min) * 100.0
        return max(0.0, min(100.0, soc))

    def get_low_power_alert(self):
        return self.stable_data["stateOfCharge"] <= 20 or self.stable_data["remainingTime"] <= 120.0

    def read(self):
        with self.lock:
            snapshot = dict(self.stable_data)
        return snapshot

    def read_raw(self):
        with self.lock:
            snapshot = dict(self.stable_raw_data)
        return snapshot
