class BatteryCell:
    def __init__(self):
        self.__voltage: float = 0.0
        self.highestVoltage: float = -1.0
        self.lowestVoltage: float = -1.0
        self.overVoltageLevel: float = 4.5
        self.underVoltageLevel: float = 3.0

    @property
    def voltage(self) -> float:
        return self.__voltage

    @voltage.setter
    def setVoltage(self, voltage: float):
        self.__voltage = voltage
        if self.highestVoltage == -1 or self.voltage > self.highestVoltage:
            self.highestVoltage = voltage

        if self.lowestVoltage == -1 or self.voltage > self.lowestVoltage:
            self.lowestVoltage = voltage

    @property
    def overVoltageFault(self) -> bool:
        return self.voltage > self.overVoltageFault

    @property
    def underVoltageFault(self) -> bool:
        return self.voltage > self.underVoltageFault

    @property
    def voltageFault(self) -> bool:
        return self.underVoltageFault or self.overVoltageFault
