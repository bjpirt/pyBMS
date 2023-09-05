from __future__ import annotations
import math
from typing import TYPE_CHECKING, Union

from hal import get_interval
from .tesla_model_s_constants import CELL_COUNT, REG_ADC_CONTROL, REG_ADC_CONVERT, \
    REG_ALERT_STATUS, REG_CB_CTRL, REG_CB_TIME, REG_DEVICE_STATUS, REG_FAULT_STATUS, \
    REG_IO_CONTROL, REG_SHDW_CONTROL, REG_CONFIG_COV, REG_CONFIG_COVT, REG_CONFIG_CUV, \
    REG_CONFIG_CUVT, REG_CONFIG_OT, REG_CONFIG_OTT, SHDW_CONTROL_VALUE
from battery import BatteryModule, BatteryCell
if TYPE_CHECKING:
    from config import Config
    from .tesla_model_s_network_gateway import TeslaModelSNetworkGateway


def _parse_raw_status_values(raw_values: bytearray) -> list[int]:
    output = []
    output.append(int(raw_values[0]))
    for i in range(0, int((len(raw_values)-1)/2)):
        output.append((raw_values[i*2 + 1] << 8) + raw_values[i*2 + 2])
    return output


def _convert_raw_module_voltage(raw: int) -> float:
    return round(raw * 100 / 49149, 3)


def _convert_raw_cell_voltage(raw: int) -> float:
    return round(raw * 6.25 / 16383, 3)


def _convert_raw_temperature(raw: int):
    try:
        temp_temp = (1.780 / ((raw + 2) / 33046) - 3.57) * 1000
        temp_calc = 1.0 / (0.0007610373573 + (0.0002728524832 * math.log(temp_temp)
                                              ) + (math.pow(math.log(temp_temp), 3) * 0.0000001022822735))

        return round(temp_calc - 273.15, 3)
    except ValueError as e:
        raise RuntimeError from e


def _convert_raw_values(raw_values: list[int]) -> list[float]:
    output = [
        _convert_raw_module_voltage(raw_values[0]),
    ]
    for raw_cell_voltage in raw_values[1:7]:
        output.append(_convert_raw_cell_voltage(raw_cell_voltage))
    output.append(_convert_raw_temperature(raw_values[7]))
    output.append(_convert_raw_temperature(raw_values[8]))

    return output


def _values_are_sane(values: list[float]) -> bool:
    return values[0] < 27 and all([v < 4.5 for v in values[1:7]])


class TeslaModelSBatteryModule(BatteryModule):
    def __init__(self, address: int, gateway: TeslaModelSNetworkGateway, config: Config) -> None:
        super().__init__(config)
        self.address: int = address
        self.__gateway: TeslaModelSNetworkGateway = gateway
        self.cell_count = 6
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

    def balance(self) -> None:
        balance_value: int = 0
        for i, cell in enumerate(self.cells):
            if cell.balancing is True:
                balance_value = balance_value | (1 << i)
        if balance_value != 0:
            self.__write_register(REG_CB_TIME, self._config.balance_time)
            self.__write_register(REG_CB_CTRL, balance_value)

    def __check_communication_time(self):
        self.comms_fault = self.__comms_timeout.ready

    def __read_module_(self) -> Union[list[int], None]:
        self.__write_register(REG_ADC_CONTROL, 0b00111101)
        self.__write_register(REG_IO_CONTROL, 0b00000011)
        self.__write_register(REG_ADC_CONVERT, 0x01)
        result = self.__read_register(REG_DEVICE_STATUS, 19)
        if result is None:
            return None
        return _parse_raw_status_values(result)

    def __read_module(self) -> None:
        for attempt in range(5):
            raw_values = self.__read_module_()

            if raw_values is not None:
                try:
                    converted_values = _convert_raw_values(raw_values[1:])
                    if _values_are_sane(converted_values):
                        if self._config.hardware_fault_detection:
                            self.__check_status(raw_values[0])
                        self.voltage = converted_values[0]
                        for cell, voltage in zip(self.cells, converted_values[1:7]):
                            cell.voltage = voltage
                        self.temperatures[0] = converted_values[7]
                        self.temperatures[1] = converted_values[8]
                        self.__comms_timeout.reset()
                        break
                    else:
                        if raw_values is not None and attempt > 0:
                            print(f"Mismatch. Attempt {attempt}")
                            print(raw_values)
                            print(converted_values)
                except RuntimeError:
                    print("Error reading data for module")
                    print("Values", [hex(c) for c in raw_values])

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
