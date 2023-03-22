import time
from typing import List
from battery import BatteryPack
from bms import Config
from hal.interval import get_interval
from . import TeslaModelSBatteryModule, TeslaModelSNetworkGateway
from .TeslaModelSConstants import *


class TeslaModelSBatteryPack(BatteryPack):

    def __init__(self,
                 gateway: TeslaModelSNetworkGateway,
                 config: Config
                 ) -> None:
        super().__init__()
        self.modules: List[TeslaModelSBatteryModule] = []
        self.__config = config
        self.__gateway: TeslaModelSNetworkGateway = gateway
        self.__setupInterval = get_interval()
        self.__setupModules()

    def update(self) -> None:
        if self.ready:
            super().update()
            if self.__config.autoBalance:
                self.__balance()
        elif self.__setupInterval.ready:
            self.__setupModules()

    def __setupModules(self) -> None:
        # Reset all of the addresses to 0x00
        for _ in range(3):
            if self.__gateway.writeRegister(BROADCAST_ADDRESS, REG_RESET, RESET_VALUE):
                break

        # Read the status register at address zero, then assign an address until no more are left
        for _ in range(100):
            if self.__gateway.readRegister(0x00, REG_DEVICE_STATUS, 1):
                nextAddress = len(self.modules) + 1
                self.__gateway.writeRegister(
                    0x00, REG_ADDRESS_CONTROL, nextAddress | 0x80)

                # Read from the new address to make sure it works and add it if it does
                readResult = self.__gateway.readRegister(
                    nextAddress, REG_ADDRESS_CONTROL, 1)

                if readResult and readResult[0] & 0b00111111 == nextAddress:
                    self.modules.append(TeslaModelSBatteryModule(
                        nextAddress, self.__gateway, self.__config))
            else:
                break

        if len(self.modules) == self.__config.moduleCount:
            self.ready = True
        else:
            self.__setupInterval.set(1)

    def __balance(self):
        lowCellVoltage = self.lowCellVoltage
        for module in self.modules:
            module.balance(lowCellVoltage)
