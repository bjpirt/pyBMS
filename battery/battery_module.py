from __future__ import annotations
import math
from .constants import COMMS, OVER_TEMPERATURE, UNDER_TEMPERATURE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import Config
    from typing import List
    from battery import BatteryCell


class BatteryModule:
    def __init__(self, config: Config):
        self.cells: List[BatteryCell] = []
        self.temperatures: List[float] = []
        self._config: Config = config
        self.__cell_count = 0

        self.__voltage: float = 0.0

        self.highest_voltage: float = float('nan')
        self.lowest_voltage: float = float('nan')

        self.highest_temperature: float = float('nan')
        self.lowest_temperature: float = float('nan')

        self.__alert: bool = False
        self.__fault: bool = False
        self.__comms_fault: bool = False

    @property
    def cell_count(self) -> int:
        return self.__cell_count

    @cell_count.setter
    def cell_count(self, count: int):
        self.__cell_count = count

    @property
    def over_temperature_alert(self) -> bool:
        return self.high_temperature > self._config.high_temperature_setpoint - self._config.temperature_warning_offset

    @property
    def under_temperature_alert(self) -> bool:
        return self.low_temperature < self._config.low_temperature_setpoint + self._config.temperature_warning_offset

    @property
    def alert(self) -> bool:
        return any((c.alert for c in self.cells)) \
            or self.over_temperature_alert or self.under_temperature_alert or self.__alert

    @alert.setter
    def alert(self, value: bool):
        self.__alert = value

    @property
    def alerts(self) -> List[str]:
        alerts = []
        for cell in self.cells:
            alerts.extend(cell.alerts)
        if self.over_temperature_alert:
            alerts.append(OVER_TEMPERATURE)
        if self.under_temperature_alert:
            alerts.append(UNDER_TEMPERATURE)
        return list(dict.fromkeys(alerts))

    @property
    def comms_fault(self) -> bool:
        return self.__comms_fault

    @comms_fault.setter
    def comms_fault(self, value: bool):
        self.__comms_fault = value

    @property
    def over_temperature_fault(self) -> bool:
        return self.high_temperature > self._config.high_temperature_setpoint

    @property
    def under_temperature_fault(self) -> bool:
        return self.low_temperature < self._config.low_temperature_setpoint

    @property
    def fault(self) -> bool:
        return any((c.fault for c in self.cells)) \
            or self.over_temperature_fault or self.under_temperature_fault \
            or self.__comms_fault or self.__fault

    @fault.setter
    def fault(self, value: bool):
        self.__fault = value

    @property
    def faults(self) -> List[str]:
        faults = []
        for cell in self.cells:
            faults.extend(cell.faults)
        if self.over_temperature_fault:
            faults.append(OVER_TEMPERATURE)
        if self.under_temperature_fault:
            faults.append(UNDER_TEMPERATURE)
        if self.comms_fault:
            faults.append(COMMS)
        return list(dict.fromkeys(faults))

    @property
    def voltage(self):
        return self.__voltage

    @voltage.setter
    def voltage(self, voltage):
        self.__voltage = voltage

        if self.voltage > self.highest_voltage or math.isnan(self.highest_voltage):
            self.highest_voltage = self.voltage

        if self.voltage < self.lowest_voltage or math.isnan(self.lowest_voltage):
            self.lowest_voltage = self.voltage

    @property
    def average_cell_voltage(self) -> float:
        return self.total_cell_voltage / len(self.cells) if len(self.cells) > 0 else 0.0

    @property
    def total_cell_voltage(self) -> float:
        return sum(self.__cell_voltages()) if len(self.cells) > 0 else 0.0

    @property
    def low_cell_voltage(self) -> float:
        return min(self.__cell_voltages()) if len(self.cells) > 0 else 0.0

    @property
    def high_cell_voltage(self) -> float:
        return max(self.__cell_voltages()) if len(self.cells) > 0 else 0.0

    @property
    def lowest_cell_voltage(self) -> float:
        return min((cell.lowest_voltage for cell in self.cells)) if len(self.cells) > 0 else 0.0

    @property
    def highest_cell_voltage(self) -> float:
        return max((cell.highest_voltage for cell in self.cells)) if len(self.cells) > 0 else 0.0

    @property
    def cell_voltage_difference(self) -> float:
        return self.high_cell_voltage - self.low_cell_voltage

    @property
    def average_temperature(self) -> float:
        if len(self.temperatures) > 0:
            return sum(self.temperatures) / len(self.temperatures)
        return 0.0

    @property
    def high_temperature(self) -> float:
        return max(self.temperatures) if len(self.temperatures) > 0 else 0.0

    @property
    def low_temperature(self) -> float:
        return min(self.temperatures) if len(self.temperatures) > 0 else 0.0

    def update(self):
        if self.high_temperature > self.highest_temperature or math.isnan(self.highest_temperature):
            self.highest_temperature = self.high_temperature

        if self.low_temperature < self.lowest_temperature or math.isnan(self.lowest_temperature):
            self.lowest_temperature = self.low_temperature

    def balance(self) -> None:
        pass

    def __cell_voltages(self):
        return [cell.voltage for cell in self.cells]

    def get_dict(self):
        return {
            "temperatures": self.temperatures,
            "voltage": self.voltage,
            "highest_voltage": self.highest_voltage,
            "lowest_voltage": self.lowest_voltage,
            "highest_temperature": self.highest_temperature,
            "lowest_temperature": self.lowest_temperature,
            "fault": self.fault,
            "faults": self.faults,
            "alert": self.alert,
            "alerts": self.alerts,
            "cells": [c.get_dict() for c in self.cells]
        }
