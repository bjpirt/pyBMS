from typing import List
from battery.BatteryPack import BatteryPack
from battery.tesla_model_s.TeslaModelSBatteryModule import TeslaModelSBatteryModule
from battery.tesla_model_s.TeslaModelSConstants import *
from battery.tesla_model_s.TeslaModelSNetworkGateway import TeslaModelSNetworkGateway

ADDRESS_REGISTER = 0x3B


class TeslaModelSBatteryPack(BatteryPack):

    def __init__(self, moduleCount: int, gateway: TeslaModelSNetworkGateway) -> None:
        super().__init__()
        self.modules: List[TeslaModelSBatteryModule] = []
        self.__moduleCount = moduleCount
        self.ready = False
        self.__gateway = gateway
        self.__setupModules()

    def update(self) -> None:
        if self.ready:
            super().update()
            self.__balance()

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
                    nextAddress, REG_DEVICE_STATUS, 1)

                if readResult and readResult[0] & 0x08 > 0:
                    self.modules.append(TeslaModelSBatteryModule(
                        nextAddress, self.__gateway))
            else:
                break

        if len(self.modules) == self.__moduleCount:
            self.ready = True

    def __balance(self):
        lowCellVoltage = self.lowCellVoltage
        for module in self.modules:
            module.balance(lowCellVoltage)
