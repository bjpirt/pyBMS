from __future__ import annotations
import math
from typing import TYPE_CHECKING
from battery.constants import BALANCE, OVER_TEMPERATURE, OVER_VOLTAGE, \
    UNDER_TEMPERATURE, UNDER_VOLTAGE
if TYPE_CHECKING:
    from typing import List, Union
    from bms import Config
    from battery import BatteryModule


class BatteryPack:
    def __init__(self, config: Config) -> None:
        self._config = config
        self.modules: List[BatteryModule] = []

        self.highest_voltage: float = -1
        self.lowest_voltage: float = -1

        self.highest_temperature: float = -1
        self.lowest_temperature: float = -1
        self.ready = False

    @property
    def has_fault(self) -> bool:
        return any((m.has_fault for m in self.modules))

    @property
    def voltage(self) -> float:
        if len(self.modules) <= 0:
            return 0.0
        return sum((module.voltage for module in self.modules)) / self._config.parallel_string_count

    @property
    def high_cell_voltage(self) -> float:
        if len(self.modules) > 0:
            return max((module.high_cell_voltage for module in self.modules))
        return 0.0

    @property
    def low_cell_voltage(self) -> float:
        if len(self.modules) > 0:
            return min((module.low_cell_voltage for module in self.modules))
        return 0.0

    @property
    def average_cell_voltage(self) -> float:
        if len(self.modules) > 0:
            return sum((module.average_cell_voltage for module in self.modules)) / len(self.modules)
        return 0.0

    @property
    def average_temperature(self) -> float:
        if len(self.modules) > 0:
            return sum((module.average_temperature for module in self.modules)) / len(self.modules)
        return 0.0

    @property
    def high_temperature(self) -> float:
        if len(self.modules) > 0:
            return max((module.high_temperature for module in self.modules))
        return 0.0

    @property
    def low_temperature(self) -> float:
        if len(self.modules) > 0:
            return min((module.low_temperature for module in self.modules))
        return 0.0

    @property
    def capacity(self) -> float:
        return self._config.module_capacity * self._config.module_count / self._config.parallel_string_count

    @property
    def cell_voltage_difference(self) -> float:
        if len(self.modules) > 0:
            return max((module.cell_voltage_difference for module in self.modules))
        return 0.0

    @property
    def alarms(self) -> Union[List[int], None]:
        alarms = []
        if self.high_cell_voltage > self._config.cell_high_voltage_setpoint:
            alarms.append(OVER_VOLTAGE)
        if self.low_cell_voltage < self._config.cell_low_voltage_setpoint:
            alarms.append(UNDER_VOLTAGE)
        if self.high_temperature > self._config.high_temperature_setpoint:
            alarms.append(OVER_TEMPERATURE)
        if self.low_temperature < self._config.low_temperature_setpoint:
            alarms.append(UNDER_TEMPERATURE)
        if self.cell_voltage_difference > self._config.max_cell_voltage_difference:
            alarms.append(BALANCE)
        return alarms if len(alarms) > 0 else None

    @property
    def warnings(self) -> Union[List[int], None]:
        warnings = []
        if self.high_cell_voltage > self._config.cell_high_voltage_setpoint - self._config.voltage_warning_offset:
            warnings.append(OVER_VOLTAGE)
        if self.low_cell_voltage < self._config.cell_low_voltage_setpoint + self._config.voltage_warning_offset:
            warnings.append(UNDER_VOLTAGE)
        if self.high_temperature > self._config.high_temperature_setpoint - self._config.temperature_warning_offset:
            warnings.append(OVER_TEMPERATURE)
        if self.low_temperature < self._config.low_temperature_setpoint + self._config.temperature_warning_offset:
            warnings.append(UNDER_TEMPERATURE)
        if self.cell_voltage_difference > self._config.max_cell_voltage_difference - self._config.voltage_difference_warning_offset:
            warnings.append(BALANCE)
        return warnings if len(warnings) > 0 else None

    def update(self) -> None:
        for module in self.modules:
            module.update()

        if self.voltage > self.highest_voltage:
            self.highest_voltage = self.voltage

        if self.voltage < self.lowest_voltage or self.lowest_voltage < 0:
            self.lowest_voltage = self.voltage

        if self.high_temperature > self.highest_temperature:
            self.highest_temperature = self.high_temperature

        if self.low_temperature < self.lowest_temperature or self.lowest_temperature < 0:
            self.lowest_temperature = self.low_temperature

    def get_dict(self):
        return {
            "ready": self.ready,
            "voltage": self.voltage,
            "highest_voltage": self.highest_voltage,
            "lowest_voltage": self.lowest_voltage,
            "highest_temperature": self.highest_temperature,
            "lowest_temperature": self.lowest_temperature,
            "current": 0,
            "state_of_charge": 0.5,
            "alarms": self.alarms,
            "warnings": self.warnings,
            "fault": self.has_fault,
            "modules": [m.get_dict() for m in self.modules]
        }
