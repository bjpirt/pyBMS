from __future__ import annotations
from typing import TYPE_CHECKING
from hal.interval import get_interval
from .led import Led
from .config import Config
from .contactor_control import ContactorControl
from .state_of_charge import StateOfCharge
if TYPE_CHECKING:
    from battery import BatteryPack


class Bms:
    def __init__(self, battery_pack: BatteryPack, config: Config):
        self.__config = config
        self.battery_pack = battery_pack
        self.contactors = ContactorControl(config)
        self.__poll_interval: float = self.__config.poll_interval
        self.__interval = get_interval()
        self.__interval.set(self.__poll_interval)
        self.__led = Led(self.__config.led_pin)
        self.__state_of_charge = StateOfCharge(
            self.battery_pack, self.__config)

    def process(self):
        if self.__interval.ready:
            self.__interval.set(self.__poll_interval)
            self.battery_pack.update()

            if self.battery_pack.has_fault or not self.battery_pack.ready:
                self.contactors.disable()
            else:
                self.contactors.enable()

        self.contactors.process()
        if self.__config.debug:
            self.print_debug()
        self.__led.process()

    @property
    def state_of_charge(self):
        return self.__state_of_charge.scaled_level

    def get_dict(self) -> dict:
        return {
            "state_of_charge": self.__state_of_charge.level,
            "contactors": self.contactors.get_dict(),
            "pack": self.battery_pack.get_dict()
        }

    def print_debug(self):
        if not self.battery_pack.ready:
            print("Battery pack not ready")
        for i, module in enumerate(self.battery_pack.modules):
            print(
                f"Module: {i} Voltage: {module.voltage} Temperature: \
                    {module.temperatures[0]} {module.temperatures[0]} Fault: {module.has_fault}")
            for j, cell in enumerate(module.cells):
                print(f"  |- Cell: {j} voltage: {cell.voltage}")
