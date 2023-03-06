import time
from battery.BatteryPack import BatteryPack
from hal import ContactorGpio
from . import ContactorControl


class Bms:
    def __init__(self, batteryPack: BatteryPack, contactorGpio: ContactorGpio, pollInterval: float = 0.5, debug: bool = False):
        self.batteryPack = batteryPack
        self.contactors = ContactorControl(contactorGpio)
        self.__pollInterval: float = pollInterval
        self.__nextPoll: float = 0
        self.__debug: bool = debug

    def process(self):
        if self.__nextPoll < time.time():
            self.__nextPoll = time.time() + self.__pollInterval
            self.batteryPack.update()

            if self.batteryPack.hasFault or not self.batteryPack.ready:
                self.contactors.disable()
            else:
                self.contactors.enable()

            self.contactors.process()
            if self.__debug:
                self.printDebug()

    def printDebug(self):
        for i, module in enumerate(self.batteryPack.modules):
            print(
                f"Module: {i} Voltage: {module.voltage} Temperature: {module.temperatures[0]} {module.temperatures[0]} Fault: {module.hasFault}")
            for j, cell in enumerate(module.cells):
                print(f"  |- Cell: {j} voltage: {cell.voltage}")
