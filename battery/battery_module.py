from __future__ import annotations
import math
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bms import Config
    from typing import List
    from battery import BatteryCell


class BatteryModule:
    def __init__(self, config: Config):
        self.cells: List[BatteryCell] = []
        self.temperatures: List[float] = []
        self._config: Config = config

        self.__voltage: float = 0.0

        self.highest_voltage: float = float('nan')
        self.lowest_voltage: float = float('nan')

        self.highest_temperature: float = float('nan')
        self.lowest_temperature: float = float('nan')

        self.__fault: bool = False

    @property
    def has_fault(self) -> bool:
        return any((c.has_fault for c in self.cells)) \
            or self.high_temperature > self._config.high_temperature_setpoint \
            or self.__fault

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
            "fault": self.has_fault,
            "cells": [c.get_dict() for c in self.cells]
        }
