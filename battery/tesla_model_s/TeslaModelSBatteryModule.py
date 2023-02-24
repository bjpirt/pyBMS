from battery.BatteryCell import BatteryCell
from battery.BatteryModule import BatteryModule
from battery.tesla_model_s.TeslaModelSNetworkGateway import TeslaModelSNetworkGateway

ADC_VALUE_REGISTER = 0x01


class TeslaModelSBatteryModule(BatteryModule):
    CELL_COUNT = 6

    def __init__(self, address, gateway: TeslaModelSNetworkGateway) -> None:
        self.__gateway: TeslaModelSNetworkGateway = gateway
        self.__address = address
        for _ in range(self.CELL_COUNT):
            self.cells.append(BatteryCell())

        super().__init__()

    def update(self) -> None:
        self.__readSensors()
        super().update()

    def __readSensors(self) -> None:
        self.__writeAdcControl(0b00111101)
        self.__writeIoControl(0b00000011)
        self.__writeAdcConversionControl(0x01)
        result = self.__gateway.readRegister(
            self.__address, ADC_VALUE_REGISTER, 20)

        # moduleVoltage = (buffer[3] * 256 + buffer[4]) * 0.0020346293922562f;

        #     for (int cell=0; cell < CELL_COUNT; cell++)
        #     {
        #       cellVoltages[cell] = (buffer[5 + (cell * 2)] * 256 + buffer[6 + (cell * 2)]) * 0.000381493f; }
        #     calculateHighLow();
        #     temperatures[0] = convertTemperature(buffer[17] * 256 + buffer[18]);
        #     temperatures[1] = convertTemperature(buffer[19] * 256 + buffer[20]);
        #     lastSuccessfulRead = millis();
        #     return 1;
        #   }
        #   return 0;
        pass

    def __writeAdcControl(self, bitmask: int):
        pass

    def __writeIoControl(self, bitmask: int):
        pass

    def __writeAdcConversionControl(self, bitmask: int):
        pass
