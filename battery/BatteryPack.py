import math
from typing import List
from battery import BatteryModule


class BatteryPack:
    def __init__(self) -> None:
        self.modules: List[BatteryModule] = []
        self.parallelStringCount: int = 1

        self.highestVoltage: float = float('nan')
        self.lowestVoltage: float = float('nan')

        self.highestTemperature: float = float('nan')
        self.lowestTemperature: float = float('nan')

    @property
    def voltage(self) -> float:
        if len(self.modules) <= 0:
            return 0.0
        return sum([module.voltage for module in self.modules]) / self.parallelStringCount

    @property
    def highCellVoltage(self) -> float:
        return max([module.highCellVoltage for module in self.modules]) if len(self.modules) > 0 else 0.0

    @property
    def lowCellVoltage(self) -> float:
        return min([module.lowCellVoltage for module in self.modules]) if len(self.modules) > 0 else 0.0

    @property
    def averageTemperature(self) -> float:
        return sum([module.averageTemperature for module in self.modules]) / len(self.modules) if len(self.modules) > 0 else 0.0

    @property
    def highTemperature(self) -> float:
        return max([module.highTemperature for module in self.modules]) if len(self.modules) > 0 else 0.0

    @property
    def lowTemperature(self) -> float:
        return min([module.lowTemperature for module in self.modules]) if len(self.modules) > 0 else 0.0

    def update(self) -> None:
        for module in self.modules:
            module.update()

        if self.voltage > self.highestVoltage or math.isnan(self.highestVoltage):
            self.highestVoltage = self.voltage

        if self.voltage < self.lowestVoltage or math.isnan(self.lowestVoltage):
            self.lowestVoltage = self.voltage

        if self.highTemperature > self.highestTemperature or math.isnan(self.highestTemperature):
            self.highestTemperature = self.highTemperature

        if self.lowTemperature < self.lowestTemperature or math.isnan(self.lowestTemperature):
            self.lowestTemperature = self.lowTemperature
