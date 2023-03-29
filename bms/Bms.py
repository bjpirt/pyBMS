from battery.BatteryPack import BatteryPack
from .Led import Led
from hal import ContactorGpio
from hal.interval import get_interval
from .Config import Config
from .ContactorControl import ContactorControl
from .StateOfCharge import StateOfCharge


class Bms:
    def __init__(self, batteryPack: BatteryPack, contactorGpio: ContactorGpio, config: Config):
        self.__config = config
        self.batteryPack = batteryPack
        self.contactors = ContactorControl(contactorGpio)
        self.__pollInterval: float = self.__config.pollInterval
        self.__interval = get_interval()
        self.__interval.set(self.__pollInterval)
        self.__led = Led(self.__config.ledPin)
        self.__stateOfCharge = StateOfCharge(self.batteryPack, self.__config)

    def process(self):
        if self.__interval.ready:
            self.__interval.set(self.__pollInterval)
            self.batteryPack.update()

            if self.batteryPack.hasFault or not self.batteryPack.ready:
                self.contactors.disable()
            else:
                self.contactors.enable()

            self.contactors.process()
            if self.__config.debug:
                self.printDebug()
        self.__led.process()

    @property
    def stateOfCharge(self):
        return self.__stateOfCharge.scaledLevel

    def getDict(self) -> dict:
        return {
            "stateOfCharge": self.__stateOfCharge.level,
            "contactors": self.contactors.getDict(),
            "pack": self.batteryPack.getDict()
        }

    def printDebug(self):
        if not self.batteryPack.ready:
            print("Battery pack not ready")
        for i, module in enumerate(self.batteryPack.modules):
            print(
                f"Module: {i} Voltage: {module.voltage} Temperature: {module.temperatures[0]} {module.temperatures[0]} Fault: {module.hasFault}")
            for j, cell in enumerate(module.cells):
                print(f"  |- Cell: {j} voltage: {cell.voltage}")
