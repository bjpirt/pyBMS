from battery.BatteryPack import BatteryPack
from battery.tesla_model_s.TeslaModelSBatteryModule import TeslaModelSBatteryModule
from battery.tesla_model_s.TeslaModelSNetworkGateway import TeslaModelSNetworkGateway

ADDRESS_REGISTER = 0x3B


class TeslaModelSBatteryPack(BatteryPack):

    def __init__(self, gateway: TeslaModelSNetworkGateway) -> None:
        super().__init__()
        self.__gateway = gateway
        self.__discoverModules()

    def update(self) -> None:
        for module in self.__modules:
            module.update()
        super().update()

    def __discoverModules(self) -> None:
        for address in range(0x01, 0x3E):
            result = self.__gateway.readRegister(address, ADDRESS_REGISTER, 1)
            if result != None:
                module = TeslaModelSBatteryModule(address, self.__gateway)
                self.__modules.append(module)
