import math
from typing import List, Union
from battery import BatteryModule
from battery.Constants import *
from bms import Config


class BatteryPack:
    def __init__(self, config: Config) -> None:
        self._config = config
        self.modules: List[BatteryModule] = []

        self.highestVoltage: float = float('nan')
        self.lowestVoltage: float = float('nan')

        self.highestTemperature: float = float('nan')
        self.lowestTemperature: float = float('nan')
        self.ready = False

    @property
    def hasFault(self) -> bool:
        return any([m.hasFault for m in self.modules])

    @property
    def voltage(self) -> float:
        if len(self.modules) <= 0:
            return 0.0
        return sum([module.voltage for module in self.modules]) / self._config.parallelStringCount

    @property
    def highCellVoltage(self) -> float:
        return max([module.highCellVoltage for module in self.modules]) if len(self.modules) > 0 else 0.0

    @property
    def lowCellVoltage(self) -> float:
        return min([module.lowCellVoltage for module in self.modules]) if len(self.modules) > 0 else 0.0

    @property
    def averageCellVoltage(self) -> float:
        if len(self.modules) <= 0:
            return 0.0
        return sum([module.averageCellVoltage for module in self.modules]) / len(self.modules)

    @property
    def averageTemperature(self) -> float:
        return sum([module.averageTemperature for module in self.modules]) / len(self.modules) if len(self.modules) > 0 else 0.0

    @property
    def highTemperature(self) -> float:
        return max([module.highTemperature for module in self.modules]) if len(self.modules) > 0 else 0.0

    @property
    def lowTemperature(self) -> float:
        return min([module.lowTemperature for module in self.modules]) if len(self.modules) > 0 else 0.0

    @property
    def capacity(self) -> float:
        return self._config.moduleCapacity * self._config.moduleCount / self._config.parallelStringCount

    @property
    def cellVoltageDifference(self) -> float:
        return max([module.cellVoltageDifference for module in self.modules]) if len(self.modules) > 0 else 0.0

    @property
    def alarms(self) -> Union[List[int], None]:
        alarms = []
        if self.highCellVoltage > self._config.cellHighVoltageSetpoint:
            alarms.append(OVER_VOLTAGE)
        if self.lowCellVoltage < self._config.cellLowVoltageSetpoint:
            alarms.append(UNDER_VOLTAGE)
        if self.highTemperature > self._config.highTemperatureSetpoint:
            alarms.append(OVER_TEMPERATURE)
        if self.lowTemperature < self._config.lowTemperatureSetpoint:
            alarms.append(UNDER_TEMPERATURE)
        if self.cellVoltageDifference > self._config.maxCellVoltageDifference:
            alarms.append(BALANCE)
        return alarms if len(alarms) > 0 else None

    @property
    def warnings(self) -> Union[List[int], None]:
        warnings = []
        if self.highCellVoltage > self._config.cellHighVoltageSetpoint - self._config.voltageWarningOffset:
            warnings.append(OVER_VOLTAGE)
        if self.lowCellVoltage < self._config.cellLowVoltageSetpoint + self._config.voltageWarningOffset:
            warnings.append(UNDER_VOLTAGE)
        if self.highTemperature > self._config.highTemperatureSetpoint - self._config.temperatureWarningOffset:
            warnings.append(OVER_TEMPERATURE)
        if self.lowTemperature < self._config.lowTemperatureSetpoint + self._config.temperatureWarningOffset:
            warnings.append(UNDER_TEMPERATURE)
        if self.cellVoltageDifference > self._config.maxCellVoltageDifference - self._config.voltageDifferenceWarningOffset:
            warnings.append(BALANCE)
        return warnings if len(warnings) > 0 else None

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

    def getDict(self):
        return {
            "ready": self.ready,
            "voltage": self.voltage,
            "highestVoltage": self.highestVoltage,
            "lowestVoltage": self.lowestVoltage,
            "highestTemperature": self.highestTemperature,
            "lowestTemperature": self.lowestTemperature,
            "alarms": self.alarms,
            "warnings": self.warnings,
            "fault": self.hasFault,
            "modules": [m.getDict() for m in self.modules]
        }
