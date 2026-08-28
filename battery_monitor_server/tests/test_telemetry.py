import pytest

from telemetry import Telemetry


def test_soc_from_voltage_is_clamped_to_battery_limits():
    telemetry = Telemetry(nominal_battery_volts=11.1, battery_max_voltage=12.6)

    assert telemetry._soc_from_voltage(10.0) == 0.0
    assert telemetry._soc_from_voltage(11.85) == pytest.approx(50.0)
    assert telemetry._soc_from_voltage(13.0) == 100.0


def test_soc_from_voltage_handles_invalid_values():
    telemetry = Telemetry()

    assert telemetry._soc_from_voltage(None) == 0.0
    assert telemetry._soc_from_voltage("not-a-number") == 0.0


def test_remaining_capacity_uses_drawn_and_regenerated_charge():
    telemetry = Telemetry(nominal_battery_amps=5.0)
    telemetry.stable_data["ampHours"] = 1.5
    telemetry.stable_data["ampHoursCharged"] = 0.25

    assert telemetry.get_remaining_capacity() == pytest.approx(3.75)


def test_remaining_time_keeps_previous_value_when_current_is_negligible():
    telemetry = Telemetry()
    telemetry.stable_data["remainingTime"] = 123.0
    telemetry.stable_data["current"] = 0.01

    assert telemetry.get_remaining_time() == 123.0


def test_update_smooths_values_and_completes_a_snapshot():
    telemetry = Telemetry(new_measure_weight=0.5)
    fields = {
        "dutyCycleNow": 0.0,
        "wattHoursCharged": 0.0,
        "tachometerAbs": 0.0,
        "tempMosfet": 30.0,
        "pidPos": 0.0,
        "id": 1.0,
        "error": 0.0,
        "voltage": 12.6,
        "current": 1.0,
        "rpm": 100.0,
        "avgMotorCurrent": 1.0,
        "ampHours": 1.0,
        "ampHoursCharged": 0.0,
        "wattHours": 1.0,
        "tachometer": 10.0,
        "tempMotor": 30.0,
    }

    for field, value in fields.items():
        telemetry.update(field, value)

    snapshot = telemetry.read()

    assert snapshot["voltage"] == pytest.approx(6.3)
    assert snapshot["stateOfCharge"] == pytest.approx(25.0)
    assert snapshot["remainingCapacity"] == pytest.approx(4.5)
    assert snapshot["lowPowerAlert"] is False
    assert telemetry.read_raw()["voltage"] == 12.6
