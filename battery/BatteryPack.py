from typing import List
from battery.BatteryModule import BatteryModule


class BatteryPack:
    def __init__(self) -> None:
        self.__modules: List[BatteryModule] = []

        self.packVoltage = 0
        self.lowestPackVoltage = 0
        self.highestPackVoltage = 0
        self.lowestTemperature = 0
        self.highestTemperature = 0
        self.averageTemperature = 0
        self.parallelStringCount = 1

    @property
    def highCellVoltage(self) -> float:
        return max([module.highCellVoltage for module in self.__modules]) if len(self.__modules) > 0 else 0.0

    @property
    def lowCellVoltage(self) -> float:
        return max([module.lowCellVoltage for module in self.__modules]) if len(self.__modules) > 0 else 0.0

    @property
    def averageCellVoltage(self) -> float:
        if len(self.__modules) > 0:
            return 0.0
        return sum([module.lowCellVoltage for module in self.__modules]) / len(self.__modules)

    def update(self) -> None:
        pass
