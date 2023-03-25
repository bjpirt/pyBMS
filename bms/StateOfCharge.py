from battery import BatteryPack
from .Config import Config


class StateOfCharge:
    def __init__(self, pack: BatteryPack, config: Config):
        self.__pack = pack
        self.__config = config

    def calculateFromVoltage(self, voltage: float) -> float:
        for lowPoint, highPoint in zip(self.__config.socLookup, self.__config.socLookup[1:]):
            if voltage > lowPoint[0] and voltage < highPoint[0]:
                return lowPoint[1] + (highPoint[1] - lowPoint[1]) * (voltage - lowPoint[0]) / (highPoint[0] - lowPoint[0])
        raise Exception("Could not calculate state of charge from voltage")

    @property
    def level(self) -> float:
        cellVoltage = self.__pack.averageCellVoltage
        return self.calculateFromVoltage(cellVoltage)

    @property
    def scaledLevel(self) -> float:
        lowOffset = self.calculateFromVoltage(
            self.__config.cellLowVoltageSetpoint)
        highOffset = self.calculateFromVoltage(
            self.__config.cellHighVoltageSetpoint)
        unscaledLevel = self.level
        return (unscaledLevel - lowOffset) / (highOffset - lowOffset)
