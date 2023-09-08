from __future__ import annotations
from typing import TYPE_CHECKING

from .battery_string import BatteryString
from .battery_module import BatteryModule

from .constants import BALANCE
if TYPE_CHECKING:
    from typing import List
    from config import Config


class BatteryPack:
    def __init__(self, config: Config) -> None:
        self._config = config
        self.modules: List[BatteryModule] = []
        self.strings: List[BatteryString] = []

        self.highest_voltage: float = -1
        self.lowest_voltage: float = -1

        self.highest_temperature: float = -1
        self.lowest_temperature: float = -1
        self.ready = False

    @property
    def series_module_count(self) -> int:
        return int(self._config.module_count / self._config.parallel_string_count)

    @property
    def series_cells(self) -> int:
        return self.series_module_count * self.modules[0].cell_count

    @property
    def max_voltage_setpoint(self) -> float:
        return self.series_cells * self._config.cell_high_voltage_setpoint

    @property
    def min_voltage_setpoint(self) -> float:
        return self.series_cells * self._config.cell_low_voltage_setpoint

    @property
    def balance_alert(self) -> bool:
        return self.cell_voltage_difference > (
            self._config.max_cell_voltage_difference - self._config.voltage_difference_warning_offset)

    @property
    def alert(self) -> bool:
        return any((m.alert for m in self.modules)) or self.balance_alert

    @property
    def alerts(self) -> List[str]:
        alerts = []
        for module in self.modules:
            alerts.extend(module.alerts)
        if self.balance_alert:
            alerts.append(BALANCE)
        return list(dict.fromkeys(alerts))

    @property
    def balance_fault(self) -> bool:
        return self.cell_voltage_difference > self._config.max_cell_voltage_difference

    @property
    def fault(self) -> bool:
        return any((m.fault for m in self.modules)) or self.balance_fault

    @property
    def faults(self) -> List[str]:
        faults = []
        for module in self.modules:
            faults.extend(module.faults)
        if self.balance_fault:
            faults.append(BALANCE)
        return list(dict.fromkeys(faults))

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

    def should_charge(self, current_state: bool) -> bool:
        if current_state is True:
            return self.high_cell_voltage < self._config.cell_high_voltage_setpoint
        else:
            return self.high_cell_voltage < (
                self._config.cell_high_voltage_setpoint - self._config.charge_hysteresis_voltage)

    def should_discharge(self, current_state: bool) -> bool:
        if current_state is True:
            return self.low_cell_voltage > self._config.cell_low_voltage_setpoint
        else:
            return self.low_cell_voltage > (
                self._config.cell_low_voltage_setpoint + self._config.charge_hysteresis_voltage)

    def update(self) -> None:
        for module in self.modules:
            module.update()

        for string in self.strings:
            string.balance()

        if self.voltage > self.highest_voltage:
            self.highest_voltage = self.voltage

        if self.voltage < self.lowest_voltage or self.lowest_voltage < 0:
            self.lowest_voltage = self.voltage

        if self.high_temperature > self.highest_temperature:
            self.highest_temperature = self.high_temperature

        if self.low_temperature < self.lowest_temperature or self.lowest_temperature < 0:
            self.lowest_temperature = self.low_temperature

    def _setup_strings(self) -> None:
        for i in range(0, len(self.modules), self.series_module_count):
            self.strings.append(BatteryString(self.modules[i:i+self.series_module_count], self._config))

    def get_dict(self):
        return {
            "ready": self.ready,
            "voltage": self.voltage,
            "highest_voltage": self.highest_voltage,
            "lowest_voltage": self.lowest_voltage,
            "highest_temperature": self.highest_temperature,
            "lowest_temperature": self.lowest_temperature,
            "fault": self.fault,
            "faults": self.faults,
            "alert": self.alert,
            "alerts": self.alerts,
            "modules": [m.get_dict() for m in self.modules]
        }
