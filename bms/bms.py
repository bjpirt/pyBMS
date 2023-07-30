from __future__ import annotations
from typing import TYPE_CHECKING
from hal.interval import get_interval
from hal import WDT
from .led import Led
from .config import Config
from .contactor_control import ContactorControl
from .state_of_charge import StateOfCharge
from .current_sensor import CurrentSensor
if TYPE_CHECKING:
    from typing import Optional
    from battery import BatteryPack


class Bms:
    def __init__(self, battery_pack: BatteryPack, config: Config, current_sensor: Optional[CurrentSensor] = None):
        self.__config = config
        self.battery_pack = battery_pack
        self.contactors = ContactorControl(config)
        self.__current_sensor = current_sensor
        self.__poll_interval: float = self.__config.poll_interval
        self.__interval = get_interval()
        self.__interval.set(self.__poll_interval)
        self.__led = Led(self.__config.led_pin)
        self.__wdt: Optional[WDT] = None
        if self.__config.wdt_timeout > 0:
            self.__wdt = WDT(timeout=self.__config.wdt_timeout)
        self.__state_of_charge = StateOfCharge(
            self.battery_pack, self.__config, self.__current_sensor)

    def process(self):
        if self.__interval.ready:
            self.__interval.set(self.__poll_interval)
            self.battery_pack.update()

            if self.battery_pack.fault or not self.battery_pack.ready:
                self.contactors.disable()
            else:
                self.contactors.enable()
            if self.__config.debug:
                self.print_debug()

        self.__state_of_charge.process()
        self.contactors.process()
        self.__led.process()
        if self.__wdt:
            self.__wdt.feed()

    @property
    def state_of_charge(self) -> float:
        return self.__state_of_charge.level_from_current

    @property
    def current(self) -> float:
        if self.__current_sensor is not None:
            return self.__current_sensor.current
        return 0.0

    def get_dict(self) -> dict:
        return {
            "voltage_state_of_charge": self.__state_of_charge.level_from_voltage,
            "current_state_of_charge": self.__state_of_charge.level_from_current,
            "current": self.current,
            "contactors": self.contactors.get_dict(),
            "pack": self.battery_pack.get_dict()
        }

    def print_debug(self):
        if not self.battery_pack.ready:
            print("Battery pack not ready")
        else:
            print(f"Modules: {len(self.battery_pack.modules)} Current: {self.current}A")
            print(f"Alerts: {self.battery_pack.alerts} Faults: {self.battery_pack.faults}")
        for i, module in enumerate(self.battery_pack.modules):
            print(
                f"Module: {i} Voltage: {module.voltage} Temperature: {(module.temperatures[0])}",
                f"{module.temperatures[1]} Alerts: {module.alerts} Faults: {module.faults}")
            for j, cell in enumerate(module.cells):
                print(f"  |- Cell: {j} voltage: {cell.voltage} Alerts: {cell.alerts} Faults: {cell.faults}")
