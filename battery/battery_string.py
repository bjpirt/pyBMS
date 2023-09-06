from typing import List
from .battery_module import BatteryModule
from config import Config


class BatteryString:
    def __init__(self, modules: List[BatteryModule], config: Config) -> None:
        self.modules = modules
        self._config = config

    def balance(self):
        if self._config.balancing_enabled:
            min_voltage = min([m.low_cell_voltage for m in self.modules])
            for module in self.modules:
                for cell in module.cells:
                    cell.balancing = cell.voltage - min_voltage >= self._config.balance_difference
                module.balance()
