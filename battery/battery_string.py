from typing import List
from hal.interval import get_interval
from .battery_module import BatteryModule
from config import Config


class BatteryString:
    def __init__(self, modules: List[BatteryModule], config: Config) -> None:
        self.modules = modules
        self._config = config
        self._balancing_state = "MEASURING"
        self._balancing_timer = get_interval()
        self._balancing_timer.set(self._config.balance_measuring_time)

    def balance(self):
        if self._config.balancing_enabled:
            if self._balancing_timer.ready:
                if self._balancing_state == "MEASURING":
                    min_voltage = min([m.low_cell_voltage for m in self.modules])
                    max_voltage = min([m.low_cell_voltage for m in self.modules])
                    for module in self.modules:
                        for cell in module.cells:
                            cell.balancing = (max_voltage > self._config.balance_voltage) and (
                                cell.voltage - min_voltage >= self._config.balance_difference)

                    self._balancing_timer.set(self._config.balance_time)
                    self._balancing_state = "BALANCING"
                else:
                    for module in self.modules:
                        for cell in module.cells:
                            cell.balancing = False
                    self._balancing_timer.set(self._config.balance_measuring_time)
                    self._balancing_state = "MEASURING"
            for module in self.modules:
                module.balance()
