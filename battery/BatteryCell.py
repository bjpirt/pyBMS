class BatteryCell:
    def __init__(self, lowCellVoltage: float = 3.6, highCellVoltage: float = 4.1):
        self.__voltage: float = 0.0
        self.highestVoltage: float = -1.0
        self.lowestVoltage: float = -1.0
        self.overVoltageFault: bool = False
        self.underVoltageFault: bool = False
        self.__lowCellVoltage = lowCellVoltage
        self.__highCellVoltage = highCellVoltage

    @property
    def hasFault(self) -> bool:
        return self.voltage < self.__lowCellVoltage or self.voltage > self.__highCellVoltage

    @property
    def voltage(self) -> float:
        return self.__voltage

    @voltage.setter
    def voltage(self, voltage: float) -> None:
        self.__voltage = voltage
        if self.highestVoltage == -1 or self.voltage > self.highestVoltage:
            self.highestVoltage = voltage

        if self.lowestVoltage == -1 or self.voltage < self.lowestVoltage:
            self.lowestVoltage = voltage
