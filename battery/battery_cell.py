from __future__ import annotations

from .constants import OVER_VOLTAGE, UNDER_VOLTAGE
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from config import Config


class BatteryCell:
    def __init__(self, config: Config):
        self.__voltage = 0.0
        self._config = config
        self.balancing = False
        self.highest_voltage = -1.0
        self.lowest_voltage = -1.0
        self.over_voltage_fault_override = False
        self.under_voltage_fault_override = False

    @property
    def over_voltage_fault(self) -> bool:
        return self.voltage >= self._config.high_voltage_fault_level or self.over_voltage_fault_override

    @property
    def under_voltage_fault(self) -> bool:
        return self.voltage <= self._config.low_voltage_fault_level or self.under_voltage_fault_override

    @property
    def fault(self) -> bool:
        return self.under_voltage_fault or self.over_voltage_fault

    @property
    def faults(self) -> List[str]:
        faults = []
        if self.under_voltage_fault:
            faults.append(UNDER_VOLTAGE)
        if self.over_voltage_fault:
            faults.append(OVER_VOLTAGE)
        return faults

    @property
    def over_voltage_alert(self) -> bool:
        return self.voltage >= self._config.high_voltage_alert_level

    @property
    def under_voltage_alert(self) -> bool:
        return self.voltage <= self._config.low_voltage_alert_level

    @property
    def alert(self) -> bool:
        return self.under_voltage_alert or self.over_voltage_alert

    @property
    def alerts(self) -> List[str]:
        alerts = []
        if self.under_voltage_alert:
            alerts.append(UNDER_VOLTAGE)
        if self.over_voltage_alert:
            alerts.append(OVER_VOLTAGE)
        return alerts

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

    def get_dict(self) -> dict:
        return {
            "voltage": self.voltage,
            "highest_voltage": self.highest_voltage,
            "lowest_voltage": self.lowest_voltage,
            "fault": self.fault,
            "faults": self.faults,
            "alert": self.alert,
            "alerts": self.alerts
        }
