import math
import time
from battery import BatteryModule, BatteryCell
from bms import Config
from . import TeslaModelSNetworkGateway
from battery.tesla_model_s.TeslaModelSConstants import *


class TeslaModelSBatteryModule(BatteryModule):
    def __init__(self, address: int, gateway: TeslaModelSNetworkGateway, config: Config) -> None:
        super().__init__(config)
        self.__gateway: TeslaModelSNetworkGateway = gateway
        self.address: int = address
        self.__lastCommunicationTime: float = float('nan')

        self.alert: bool = False

        for _ in range(CELL_COUNT):
            self.cells.append(BatteryCell(config))

        for _ in range(2):
            self.temperatures.append(float("nan"))

    def update(self) -> None:
        self.__readModule()
        self.__checkCommunicationTime()
        super().update()

    def balance(self, lowCellVoltage: float) -> None:
        if self.highCellVoltage > self._config.balanceVoltage and self.highCellVoltage - self.lowCellVoltage > self._config.balanceDifference:
            balanceValue: int = 0
            for i, cell in enumerate(self.cells):
                if cell.voltage > lowCellVoltage:
                    balanceValue = balanceValue | (1 << i)
            if balanceValue != 0:
                self.__writeRegister(REG_CB_TIME, self._config.balanceTime)
                self.__writeRegister(REG_CB_CTRL, balanceValue)

    def __checkCommunicationTime(self):
        # TODO: Use hal time abstraction
        self.__fault = time.time() - self.__lastCommunicationTime > self._config.commsTimeout

    def __readModule(self) -> None:
        self.__writeRegister(REG_ADC_CONTROL, 0b00111101)
        self.__writeRegister(REG_IO_CONTROL, 0b00000011)
        self.__writeRegister(REG_ADC_CONVERT, 0x01)
        result = self.__readRegister(REG_DEVICE_STATUS, 19)

        if result != None:
            self.__checkStatus(result[REG_DEVICE_STATUS])
            self.__updateModuleVoltage(result[REG_GPAI:REG_GPAI+2])
            self.__updateCellVoltages(result[REG_VCELL1:REG_VCELL1+12])
            self.__updateTemperature(
                0, result[REG_TEMPERATURE1:REG_TEMPERATURE1+2])
            self.__updateTemperature(
                1, result[REG_TEMPERATURE2:REG_TEMPERATURE2+2])
            self.__lastCommunicationTime = time.time()

    def __readModuleStatus(self):
        result = self.__readRegister(REG_ALERT_STATUS, 4)

        if result != None:
            self.alert = bool(result[0])
            self.fault = bool(result[1])
            for i, cell in enumerate(self.cells):
                cell.overVoltageFault = result[2] & (1 << i) > 0
            for i, cell in enumerate(self.cells):
                cell.underVoltageFault = result[3] & (1 << i) > 0
            self.__lastCommunicationTime = time.time()

    def __writeRegister(self, register: int, value: int):
        return self.__gateway.writeRegister(self.address, register, value)

    def __readRegister(self, register: int, length: int):
        return self.__gateway.readRegister(self.address, register, length)

    def __checkStatus(self, status: int):
        if status & 0b01100000 == 0:
            self.alert = False
            self.fault = False
            for cell in self.cells:
                cell.overVoltageFault = False
                cell.underVoltageFault = False
        else:
            self.__readModuleStatus()

    def __updateModuleVoltage(self, gpai: bytearray):
        self.voltage = round((gpai[0] * 256 + gpai[1]) * 100 / 49149, 3)

    def __updateCellVoltages(self, vcells: bytearray):
        for i in range(0, int(len(vcells)/2)):
            self.__updateCellVoltage(i, vcells[i*2:i*2+2])

    def __updateCellVoltage(self, cellNum: int, vcell: bytearray):
        self.cells[cellNum].voltage = round(
            (vcell[0] * 256 + vcell[1]) * 6.25 / 16383, 3)

    def __updateTemperature(self, id: int, temp: bytearray):
        try:
            tempTemp = (
                1.780 / ((temp[0] * 256 + temp[1] + 2) / 33046) - 3.57) * 1000
            tempCalc = 1.0 / (0.0007610373573 + (0.0002728524832 * math.log(tempTemp)
                                                 ) + (math.pow(math.log(tempTemp), 3) * 0.0000001022822735))

            self.temperatures[id] = round(tempCalc - 273.15, 3)
        except:
            print("Error calculating temperature", temp)
