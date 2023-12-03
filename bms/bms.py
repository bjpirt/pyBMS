from __future__ import annotations
from typing import TYPE_CHECKING

from .bms_interface import BmsInterface
from hal.interval import get_interval
from hal import WDT
from .led import Led
from config import Config
from .contactor_control import ContactorControl
from .state_of_charge import StateOfCharge
from .current_sensor import CurrentSensor
if TYPE_CHECKING:
    from typing import Optional
    from battery import BatteryPack


class Bms(BmsInterface):
    def __init__(self, battery_pack: BatteryPack, config: Config, current_sensor: Optional[CurrentSensor] = None):
        super().__init__(battery_pack)
        self.__config = config
        self.battery_pack = battery_pack
        if self.__config.contactor_control_enabled:
            self.__contactors = ContactorControl(config)
        self.__current_sensor = current_sensor
        self.__poll_interval: float = self.__config.poll_interval
        self.__interval = get_interval()
        self.__interval.set(self.__poll_interval)
        self.__led = Led(self.__config.led_pin)
        self.__discharging_enabled = True
        self.__charging_timer = get_interval()
        self.__charging_timer.set(self.__config.charge_hysteresis_time)
        self.__charge_current = self.__config.max_charge_current
        self.__discharging_timer = get_interval()
        self.__discharging_timer.set(self.__config.charge_hysteresis_time)
        self.__wdt: Optional[WDT] = None
        if self.__config.wdt_timeout > 0:
            self.__wdt = WDT(timeout=self.__config.wdt_timeout)
        self.__state_of_charge = StateOfCharge(
            self.battery_pack, self.__config, self.__current_sensor)

    def process(self):
        if self.__interval.ready:
            self.__interval.set(self.__poll_interval)
            self.battery_pack.update()

            if self.__config.contactor_control_enabled:
                if self.battery_pack.fault or not self.battery_pack.ready:
                    self.__contactors.disable()
                else:
                    self.__contactors.enable()

            if self.__config.debug:
                self.print_debug()

        self.__state_of_charge.process()

        if self.__config.contactor_control_enabled:
            self.__contactors.process()

        self.__led.process()
        if self.__wdt:
            self.__wdt.feed()

    @property
    def state_of_charge(self) -> float:
        if self.__config.current_sensor_soc:
            return self.__state_of_charge.level_from_current
        return self.__state_of_charge.scaled_level_from_voltage

    @property
    def current(self) -> float:
        if self.__current_sensor is not None:
            return self.__current_sensor.current
        return 0.0

    @property
    def charge_current_setpoint(self) -> float:
        voltage_difference = self.battery_pack.high_cell_voltage - \
            self.__config.cell_high_voltage_setpoint
        if voltage_difference > 0:
            scale_factor = 0.5

            # Scale back the charge current in proportion to how much the voltage is over the threshold
            # If the voltage difference is > 0.25V then set the charge current to 50% of actual
            max_difference = 0.25
            most_reduction = 0.5
            # If the voltage is not much over (0.025V), then set the charge current to 90% of actual
            min_difference = 0.025
            least_reduction = 0.9

            if voltage_difference >= max_difference:
                scale_factor = most_reduction
            elif voltage_difference < min_difference:
                scale_factor = least_reduction
            else:
                scale_factor = most_reduction + ((voltage_difference - min_difference) /
                                                 (max_difference - min_difference)) * (least_reduction - most_reduction)

            self.__charge_current = self.current * scale_factor
        elif voltage_difference <= -0.02:
            self.__charge_current = min(
                self.__charge_current * 1.1, self.__config.max_charge_current)
        return self.__charge_current

    @property
    def discharge_current_setpoint(self) -> float:
        self.__discharging_enabled = self.battery_pack.should_discharge(
            self.__discharging_enabled)
        if self.__discharging_enabled is True:
            if self.__discharging_timer.ready:
                return self.__config.max_discharge_current
        else:
            self.__discharging_timer.reset()
        return 0

    def get_dict(self) -> dict:
        return {
            "voltage_state_of_charge": self.__state_of_charge.scaled_level_from_voltage,
            "current_state_of_charge": self.__state_of_charge.level_from_current,
            "current": self.current,
            "pack": self.battery_pack.get_dict()
        }

    def print_debug(self):
        if not self.battery_pack.ready:
            print("Battery pack not ready")
        else:
            print(
                f"Modules: {len(self.battery_pack.modules)} Current: {self.current}A")
            print(
                f"Alerts: {self.battery_pack.alerts} Faults: {self.battery_pack.faults}")
        for i, module in enumerate(self.battery_pack.modules):
            print(
                f"Module: {i} Voltage: {module.voltage} Temperature: {(module.temperatures[0])}",
                f"{module.temperatures[1]} Alerts: {module.alerts} Faults: {module.faults}")
            for j, cell in enumerate(module.cells):
                balancing = "B" if cell.balancing else " "
                print(
                    f"  |- Cell:{balancing}{j} voltage: {cell.voltage} Alerts: {cell.alerts} Faults: {cell.faults}")
