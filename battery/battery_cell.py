from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bms import Config


class BatteryCell:
    def __init__(self, config: Config):
        self.__voltage = 0.0
        self.highest_voltage = -1.0
        self.lowest_voltage = -1.0
        self.over_voltage_fault = False
        self.under_voltage_fault = False
        self._config = config

    @property
    def has_fault(self) -> bool:
        return self.voltage < self._config.cell_low_voltage_setpoint or \
            self.voltage > self._config.cell_high_voltage_setpoint

    @property
    def voltage(self) -> float:
        return self.__voltage

    @voltage.setter
    def voltage(self, voltage: float) -> None:
        self.__voltage = voltage
        if self.highest_voltage == -1 or self.voltage > self.highest_voltage:
            self.highest_voltage = voltage

        if self.lowest_voltage == -1 or self.voltage < self.lowest_voltage:
            self.lowest_voltage = voltage

    def get_dict(self):
        return {
            "voltage": self.voltage,
            "highest_voltage": self.highest_voltage,
            "lowest_voltage": self.lowest_voltage,
            "over_voltage_fault": self.over_voltage_fault,
            "under_voltage_fault": self.under_voltage_fault,
            "fault": self.has_fault
        }
