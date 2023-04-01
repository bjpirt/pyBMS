from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from battery import BatteryPack
    from .config import Config


class StateOfCharge:
    def __init__(self, pack: BatteryPack, config: Config):
        self.__pack = pack
        self.__config = config

    def calculate_from_voltage(self, voltage: float) -> float:
        for low_point, high_point in zip(self.__config.soc_lookup, self.__config.soc_lookup[1:]):
            if voltage > low_point[0] and voltage < high_point[0]:
                return low_point[1] + (high_point[1] - low_point[1]) * (voltage - low_point[0]) / (high_point[0] - low_point[0])
        raise Exception("Could not calculate state of charge from voltage")

    @property
    def level(self) -> float:
        return self.calculate_from_voltage(self.__pack.average_cell_voltage)

    @property
    def scaled_level(self) -> float:
        low_offset = self.calculate_from_voltage(
            self.__config.cell_low_voltage_setpoint)
        high_offset = self.calculate_from_voltage(
            self.__config.cell_high_voltage_setpoint)
        unscaled_level = self.level
        return (unscaled_level - low_offset) / (high_offset - low_offset)