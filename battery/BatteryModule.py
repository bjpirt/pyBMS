from typing import List
from battery.BatteryCell import BatteryCell


class BatteryModule:
    def __init__(self):
        self.__cells: List[BatteryCell] = []

        self.status = 0
        self.alerts = []
        self.faults = []
        self.faultStatus = 0
        self.balanceTime = 0

        self.moduleVoltage = 0
        self.highestModuleVoltage: float = -1
        self.lowestModuleVoltage: float = -1

        self.temperatures = []
        self.averageTemperature = 0
        self.highTemperature = 0
        self.lowTemperature = 0
        self.highestTemperature = 0
        self.lowestTemperature = 0
        self.lastSuccessfulRead = 0

    @property
    def averageCellVoltage(self) -> float:
        return self.totalCellVoltage / len(self.__cells) if len(self.__cells) > 0 else 0.0

    @property
    def totalCellVoltage(self) -> float:
        return sum(self.__cellVoltages()) if len(self.__cells) > 0 else 0.0

    @property
    def lowCellVoltage(self) -> float:
        return min(self.__cellVoltages()) if len(self.__cells) > 0 else 0.0

    @property
    def highCellVoltage(self) -> float:
        return max(self.__cellVoltages()) if len(self.__cells) > 0 else 0.0

    @property
    def lowestCellVoltage(self) -> float:
        return min([cell.lowestVoltage for cell in self.__cells]) if len(self.__cells) > 0 else 0.0

    @property
    def highestCellVoltage(self) -> float:
        return max([cell.highestVoltage for cell in self.__cells]) if len(self.__cells) > 0 else 0.0

    # @property
    # def moduleVoltage(self) -> float:
    #     return sum(self.__cellVoltages()) if len(self.__cells) > 0 else 0.0

    def update(self):
        if self.moduleVoltage > self.highestModuleVoltage or self.highestModuleVoltage == -1:
            self.highestModuleVoltage = self.moduleVoltage

        if self.moduleVoltage < self.lowestModuleVoltage or self.lowestModuleVoltage == -1:
            self.lowestModuleVoltage = self.moduleVoltage

    def __cellVoltages(self):
        return [cell.voltage for cell in self.__cells]
