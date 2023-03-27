import math
from typing import List
from battery import BatteryCell
from bms import Config


class BatteryModule:
    def __init__(self, config: Config):
        self.cells: List[BatteryCell] = []
        self.temperatures: List[float] = []
        self._config: Config = config

        self.__voltage: float = 0.0

        self.highestVoltage: float = float('nan')
        self.lowestVoltage: float = float('nan')

        self.highestTemperature: float = float('nan')
        self.lowestTemperature: float = float('nan')

        self.__fault: bool = False

    @property
    def hasFault(self) -> bool:
        return any([c.hasFault for c in self.cells]) or self.highTemperature > self._config.highTemperatureSetpoint or self.__fault

    @property
    def voltage(self):
        return self.__voltage

    @voltage.setter
    def voltage(self, voltage):
        self.__voltage = voltage

        if self.voltage > self.highestVoltage or math.isnan(self.highestVoltage):
            self.highestVoltage = self.voltage

        if self.voltage < self.lowestVoltage or math.isnan(self.lowestVoltage):
            self.lowestVoltage = self.voltage

    @property
    def averageCellVoltage(self) -> float:
        return self.totalCellVoltage / len(self.cells) if len(self.cells) > 0 else 0.0

    @property
    def totalCellVoltage(self) -> float:
        return sum(self.__cellVoltages()) if len(self.cells) > 0 else 0.0

    @property
    def lowCellVoltage(self) -> float:
        return min(self.__cellVoltages()) if len(self.cells) > 0 else 0.0

    @property
    def highCellVoltage(self) -> float:
        return max(self.__cellVoltages()) if len(self.cells) > 0 else 0.0

    @property
    def lowestCellVoltage(self) -> float:
        return min([cell.lowestVoltage for cell in self.cells]) if len(self.cells) > 0 else 0.0

    @property
    def highestCellVoltage(self) -> float:
        return max([cell.highestVoltage for cell in self.cells]) if len(self.cells) > 0 else 0.0

    @property
    def cellVoltageDifference(self) -> float:
        return self.highCellVoltage - self.lowCellVoltage

    @property
    def averageTemperature(self) -> float:
        return sum(self.temperatures) / len(self.temperatures) if len(self.temperatures) > 0 else 0.0

    @property
    def highTemperature(self) -> float:
        return max(self.temperatures) if len(self.temperatures) > 0 else 0.0

    @property
    def lowTemperature(self) -> float:
        return min(self.temperatures) if len(self.temperatures) > 0 else 0.0

    def update(self):
        if self.highTemperature > self.highestTemperature or math.isnan(self.highestTemperature):
            self.highestTemperature = self.highTemperature

        if self.lowTemperature < self.lowestTemperature or math.isnan(self.lowestTemperature):
            self.lowestTemperature = self.lowTemperature

    def __cellVoltages(self):
        return [cell.voltage for cell in self.cells]

    def getDict(self):
        return {
            "temperatures": self.temperatures,
            "voltage": self.voltage,
            "highestVoltage": self.highestVoltage,
            "lowestVoltage": self.lowestVoltage,
            "highestTemperature": self.highestTemperature,
            "lowestTemperature": self.lowestTemperature,
            "fault": self.hasFault,
            "cells": [c.getDict() for c in self.cells]
        }
