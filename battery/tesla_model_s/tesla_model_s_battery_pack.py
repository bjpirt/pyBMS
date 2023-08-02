from __future__ import annotations
from typing import TYPE_CHECKING
from battery import BatteryPack
from hal.interval import get_interval
from . import TeslaModelSBatteryModule
from .tesla_model_s_constants import BROADCAST_ADDRESS, REG_ADDRESS_CONTROL, REG_DEVICE_STATUS, \
    REG_RESET, RESET_VALUE
if TYPE_CHECKING:
    from . import TeslaModelSNetworkGateway
    from bms import Config


class TeslaModelSBatteryPack(BatteryPack):

    def __init__(self,
                 gateway: TeslaModelSNetworkGateway,
                 config: Config
                 ) -> None:
        super().__init__(config)
        self.modules = []
        self.__gateway: TeslaModelSNetworkGateway = gateway
        self.__setup_interval = get_interval()
        self.__setup_modules()

    def update(self) -> None:
        if self.ready:
            super().update()
            if self._config.auto_balance:
                self.__balance()
        elif self.__setup_interval.ready:
            self.__setup_modules()

    def __setup_modules(self) -> None:
        # Reset all of the addresses to 0x00
        for _ in range(3):
            if self.__gateway.write_register(BROADCAST_ADDRESS, REG_RESET, RESET_VALUE):
                break

        # Read the status register at address zero, then assign an address until no more are left
        for _ in range(100):
            if self.__gateway.read_register(0x00, REG_DEVICE_STATUS, 1):
                next_address = len(self.modules) + 1
                self.__gateway.write_register(
                    0x00, REG_ADDRESS_CONTROL, next_address | 0x80)

                # Read from the new address to make sure it works and add it if it does
                read_result = self.__gateway.read_register(
                    next_address, REG_ADDRESS_CONTROL, 1)

                if read_result and read_result[0] & 0b00111111 == next_address:
                    module = TeslaModelSBatteryModule(
                        next_address, self.__gateway, self._config)
                    module.clearFaults()
                    module.update()
                    self.modules.append(module)
            else:
                break

        if len(self.modules) == self._config.module_count:
            self.ready = True
        else:
            self.__setup_interval.set(1)

    def __balance(self):
        low_cell_voltage = self.low_cell_voltage
        for module in self.modules:
            module.balance(low_cell_voltage)
