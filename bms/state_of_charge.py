from __future__ import annotations
from typing import TYPE_CHECKING

from hal import get_interval
if TYPE_CHECKING:
    from typing import Optional
    from bms.current_sensor.current_sensor import CurrentSensor
    from battery import BatteryPack
    from config import Config


class StateOfCharge:
    def __init__(self, pack: BatteryPack, config: Config, current_sensor: Optional[CurrentSensor] = None):
        self.__pack = pack
        self.__current_sensor = current_sensor
        self.__interval = get_interval()
        self.__interval.set(0.5)
        self.__config = config
        self.__total_capacity = self.__config.module_capacity * self.__config.parallel_string_count * 3600
        self.__available_capacity = self.available_capacity
        self.__remaining_amp_seconds = 0.0
        self.__initialised = False

    def __reset(self):
        self.__remaining_amp_seconds = self.__available_capacity

    def __initialise_from_voltage(self):
        voltage_soc = self.scaled_level_from_voltage
        self.__remaining_amp_seconds = self.__available_capacity * voltage_soc

    def __calculate_from_voltage(self, voltage: float) -> float:
        """
        Calculate the state of charge based on the charge curve in the config
        """
        if voltage <= self.__config.soc_lookup[0][0]:
            return self.__config.soc_lookup[0][1]
        if voltage >= self.__config.soc_lookup[-1][0]:
            return self.__config.soc_lookup[-1][1]
        for low_point, high_point in zip(self.__config.soc_lookup, self.__config.soc_lookup[1:]):
            if voltage >= low_point[0] and voltage < high_point[0]:
                return low_point[1] + (high_point[1] - low_point[1]) * (
                    voltage - low_point[0]) / (high_point[0] - low_point[0])
        print(f"Could not calculate state of charge. Voltage: {voltage}, SOC Lookup: {self.__config.soc_lookup}")
        raise ValueError("Could not calculate state of charge from voltage")

    def process(self):
        if not self.__initialised and self.__pack.ready:
            self.__initialise_from_voltage()
            self.__initialised = True

        if self.__current_sensor is None:
            return

        if self.__pack.ready and self.__interval.ready and self.__current_sensor.ready:
            self.__interval.reset()
            current = self.__current_sensor.read()
            self.__remaining_amp_seconds = self.__remaining_amp_seconds + (current * 0.5)
            if self.__remaining_amp_seconds > self.__available_capacity:
                self.__reset()
            if self.__remaining_amp_seconds < 0:
                self.__remaining_amp_seconds = 0

    @property
    def level_from_current(self) -> float:
        if self.__current_sensor is None or self.__current_sensor.ready is False:
            return self.scaled_level_from_voltage
        return self.__remaining_amp_seconds / self.__available_capacity

    @property
    def scaled_level_from_voltage(self) -> float:
        low_offset = self.__calculate_from_voltage(self.__config.cell_low_voltage_setpoint)
        high_offset = self.__calculate_from_voltage(self.__config.cell_high_voltage_setpoint)
        unscaled_level = self.__calculate_from_voltage(self.__pack.average_cell_voltage)
        if unscaled_level <= low_offset:
            return 0
        if unscaled_level >= high_offset:
            return 1
        return (unscaled_level - low_offset) / (high_offset - low_offset)

    @property
    def available_capacity(self) -> float:
        low_offset = self.__calculate_from_voltage(self.__config.cell_low_voltage_setpoint)
        high_offset = self.__calculate_from_voltage(self.__config.cell_high_voltage_setpoint)
        available_percent = high_offset - low_offset
        return available_percent * self.__total_capacity
