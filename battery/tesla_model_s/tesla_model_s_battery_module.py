from __future__ import annotations
import math
from typing import TYPE_CHECKING

from hal import get_interval
from .tesla_model_s_constants import CELL_COUNT, REG_ADC_CONTROL, REG_ADC_CONVERT, \
    REG_ALERT_STATUS, REG_CB_CTRL, REG_CB_TIME, REG_DEVICE_STATUS, REG_FAULT_STATUS, \
    REG_GPAI, REG_IO_CONTROL, REG_SHDW_CONTROL, REG_TEMPERATURE1, REG_TEMPERATURE2, \
    REG_VCELL1, REG_CONFIG_COV, REG_CONFIG_COVT, REG_CONFIG_CUV, REG_CONFIG_CUVT, \
    REG_CONFIG_OT, REG_CONFIG_OTT, SHDW_CONTROL_VALUE
from .. import BatteryModule, BatteryCell
if TYPE_CHECKING:
    from bms import Config
    from .tesla_model_s_network_gateway import TeslaModelSNetworkGateway


class TeslaModelSBatteryModule(BatteryModule):
    def __init__(self, address: int, gateway: TeslaModelSNetworkGateway, config: Config) -> None:
        super().__init__(config)
        self.address: int = address
        self.__gateway: TeslaModelSNetworkGateway = gateway
        self.__comms_timeout = get_interval()
        self.__comms_timeout.set(config.comms_timeout)

        for _ in range(CELL_COUNT):
            self.cells.append(BatteryCell(config))

        for _ in range(2):
            self.temperatures.append(float("nan"))

        if config.hardware_fault_detection:
            self.set_bms_cov(config.cell_high_voltage_setpoint +
                             config.voltage_hardware_offset)

            self.set_bms_cuv(config.cell_low_voltage_setpoint -
                             config.voltage_hardware_offset)

            self.set_bms_ot(int(config.high_temperature_setpoint))

    def update(self) -> None:
        self.__read_module()
        self.__check_communication_time()
        super().update()

    def balance(self, low_cell_voltage: float) -> None:
        if self.high_cell_voltage > self._config.balance_voltage and \
                self.high_cell_voltage - self.low_cell_voltage > self._config.balance_difference:
            balance_value: int = 0
            for i, cell in enumerate(self.cells):
                if cell.voltage > low_cell_voltage:
                    balance_value = balance_value | (1 << i)
            if balance_value != 0:
                self.__write_register(REG_CB_TIME, self._config.balance_time)
                self.__write_register(REG_CB_CTRL, balance_value)

    def __check_communication_time(self):
        self.comms_fault = self.__comms_timeout.ready

    def __read_module(self) -> None:
        self.__write_register(REG_ADC_CONTROL, 0b00111101)
        self.__write_register(REG_IO_CONTROL, 0b00000011)
        self.__write_register(REG_ADC_CONVERT, 0x01)
        result = self.__read_register(REG_DEVICE_STATUS, 19)

        if result is not None:
            if self._config.hardware_fault_detection:
                self.__check_status(result[REG_DEVICE_STATUS])
            self.__update_module_voltage(result[REG_GPAI:REG_GPAI+2])
            self.__update_cell_voltages(result[REG_VCELL1:REG_VCELL1+12])
            self.__update_temperature(
                0, result[REG_TEMPERATURE1:REG_TEMPERATURE1+2])
            self.__update_temperature(
                1, result[REG_TEMPERATURE2:REG_TEMPERATURE2+2])
            self.__comms_timeout.reset()

    def __read_module_status(self):
        result = self.__read_register(REG_ALERT_STATUS, 4)

        if result is not None:
            self.alert = bool(result[0])
            self.fault = bool(result[1])
            for i, cell in enumerate(self.cells):
                cell.over_voltage_fault_override = result[2] & (1 << i) > 0
            for i, cell in enumerate(self.cells):
                cell.under_voltage_fault_override = result[3] & (1 << i) > 0
            self.__comms_timeout.reset()

    def __write_register(self, register: int, value: int, set_shadow_control=False):
        if set_shadow_control:
            self.__gateway.write_register(
                self.address, REG_SHDW_CONTROL, SHDW_CONTROL_VALUE)
        return self.__gateway.write_register(self.address, register, value)

    def __read_register(self, register: int, length: int):
        return self.__gateway.read_register(self.address, register, length)

    def __check_status(self, status: int):
        if status & 0b01100000 == 0:
            self.alert = False
            self.fault = False
            for cell in self.cells:
                cell.over_voltage_fault_override = False
                cell.under_voltage_fault_override = False
        else:
            self.__read_module_status()

    def __update_module_voltage(self, gpai: bytearray):
        self.voltage = round((gpai[0] * 256 + gpai[1]) * 100 / 49149, 3)

    def __update_cell_voltages(self, vcells: bytearray):
        for i in range(0, int(len(vcells)/2)):
            self.__update_cell_voltage(i, vcells[i*2:i*2+2])

    def __update_cell_voltage(self, cell_id: int, vcell: bytearray):
        self.cells[cell_id].voltage = round(
            (vcell[0] * 256 + vcell[1]) * 6.25 / 16383, 3)

    def __update_temperature(self, temp_id: int, temp: bytearray):
        try:
            temp_temp = (
                1.780 / ((temp[0] * 256 + temp[1] + 2) / 33046) - 3.57) * 1000
            temp_calc = 1.0 / (0.0007610373573 + (0.0002728524832 * math.log(temp_temp)
                                                  ) + (math.pow(math.log(temp_temp), 3) * 0.0000001022822735))

            self.temperatures[temp_id] = round(temp_calc - 273.15, 3)
        except ValueError:
            print("Error calculating temperature", temp)

    def clearFaults(self):
        self.__write_register(REG_ALERT_STATUS, 0x80)
        self.__write_register(REG_ALERT_STATUS, 0x00)
        self.__write_register(REG_ALERT_STATUS, 0x00)
        self.__write_register(REG_FAULT_STATUS, 0x08)
        self.__write_register(REG_FAULT_STATUS, 0x00)
        self.__write_register(REG_FAULT_STATUS, 0x00)

    def set_bms_cov(self, voltage: float, seconds=1.0) -> None:
        cov = int((voltage - 2) * 20)
        self.__write_register(REG_CONFIG_COV, cov, True)
        covt = int(seconds * 10)
        self.__write_register(REG_CONFIG_COVT, covt | 0b10000000, True)

    def set_bms_cuv(self, voltage: float, seconds=1.0) -> None:
        cuv = int((voltage - 0.7) * 10)
        self.__write_register(REG_CONFIG_CUV, cuv, True)
        cuvt = int(seconds * 10)
        self.__write_register(REG_CONFIG_CUVT, cuvt | 0b10000000, True)

    def set_bms_ot(self, temperature: int, seconds=1.0) -> None:
        ot = int(((temperature - 40) / 5) + 1)
        self.__write_register(REG_CONFIG_OT, ot, True)
        ott = int(seconds * 100)
        self.__write_register(REG_CONFIG_OTT, ott, True)
