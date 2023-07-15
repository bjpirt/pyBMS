from __future__ import annotations
from typing import TYPE_CHECKING
from .constants import BALANCE
if TYPE_CHECKING:
    from typing import List
    from bms import Config
    from . import BatteryModule


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
            "fault": self.fault,
            "faults": self.faults,
            "alert": self.alert,
            "alerts": self.alerts,
            "modules": [m.get_dict() for m in self.modules]
        }
