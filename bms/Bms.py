from battery.BatteryPack import BatteryPack
from .Led import Led
from hal import ContactorGpio
from hal.interval import get_interval
from . import ContactorControl


class Bms:
    def __init__(self, batteryPack: BatteryPack, contactorGpio: ContactorGpio, pollInterval: float = 0.5, debug: bool = False, ledPin: int = 18):
        self.batteryPack = batteryPack
        self.contactors = ContactorControl(contactorGpio)
        self.__pollInterval: float = pollInterval
        self.__interval = get_interval()
        self.__interval.set(self.__pollInterval)
        self.__debug: bool = debug
        self.__led = Led(ledPin)

    def process(self):
        if self.__interval.ready:
            self.__interval.set(self.__pollInterval)
            self.batteryPack.update()

            if self.batteryPack.hasFault or not self.batteryPack.ready:
                self.contactors.disable()
            else:
                self.contactors.enable()

            self.contactors.process()
            if self.__debug:
                self.printDebug()
        self.__led.process()

    def printDebug(self):
        if not self.batteryPack.ready:
            print("Battery pack not ready")
        for i, module in enumerate(self.batteryPack.modules):
            print(
                f"Module: {i} Voltage: {module.voltage} Temperature: {module.temperatures[0]} {module.temperatures[0]} Fault: {module.hasFault}")
            for j, cell in enumerate(module.cells):
                print(f"  |- Cell: {j} voltage: {cell.voltage}")
