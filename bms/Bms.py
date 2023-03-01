from battery.BatteryPack import BatteryPack
from hal import ContactorGpio
from . import ContactorControl


class Bms:
    def __init__(self, batteryPack: BatteryPack, contactorGpio: ContactorGpio):
        self.batteryPack = batteryPack
        self.contactors = ContactorControl(contactorGpio)

    def process(self):
        self.batteryPack.update()
        
        if self.batteryPack.hasError or not self.batteryPack.ready:
            self.contactors.disable()
        else:
            self.contactors.enable()

        self.contactors.process()
