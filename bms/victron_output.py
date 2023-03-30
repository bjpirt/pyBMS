from battery.constants import *
from hal.interval import get_interval
from .bms import Bms


class CanMessage:
    def __init__(self, msg_id: int) -> None:
        self.__id: int = msg_id
        self.__message = bytearray()

    def add_int(self, value: int) -> None:
        self.__message.append(value & 0xFF)
        self.__message.append((value >> 8) & 0xFF)

    def add_byte(self, value: int) -> None:
        self.__message.append(value & 0xFF)

    def add_string(self, value: str) -> None:
        self.__message.extend(map(ord, value))

    def send(self, can) -> None:
        for _ in range(8 - len(self.__message)):
            self.__message.append(0)
        can.send(self.__message, self.__id)


class VictronOutput:
    def __init__(self, can, bms: Bms, interval: float) -> None:
        self.__can = can
        self.__bms = bms
        self.__interval = get_interval()
        self.__interval.set(interval)

    def process(self):
        if self.__interval.ready and self.__bms.battery_pack.ready:
            self.send()
            self.__interval.reset()

    def send(self) -> None:
        self.send_message_1()
        self.send_message_2()
        self.send_message_3()
        self.send_message_4()
        self.send_message_5()
        self.send_message_6()
        self.send_message_7()
        self.send_message_8()
        self.send_message_9()

    def send_message_1(self) -> None:
        """
        Sends:
            Bytes 0, 1 - settings.StoreVsetpoint * settings.Scells ??
            Bytes 2, 3 - Charge current
            Bytes 4, 5 - Discharge current
            Bytes 6, 7 - DischVsetpoint * settings.Scells ??

        msg.buf[0] = lowByte(uint16_t((settings.StoreVsetpoint * settings.Scells ) * 10));
        msg.buf[1] = highByte(uint16_t((settings.StoreVsetpoint * settings.Scells ) * 10));
        msg.buf[2] = lowByte(chargecurrent);
        msg.buf[3] = highByte(chargecurrent);
        msg.buf[4] = lowByte(discurrent );
        msg.buf[5] = highByte(discurrent);
        msg.buf[6] = lowByte(uint16_t((settings.DischVsetpoint * settings.Scells) * 10));
        msg.buf[7] = highByte(uint16_t((settings.DischVsetpoint * settings.Scells) * 10));
        """
        message = CanMessage(0x351)
        message.add_int(0)
        message.add_int(0)
        message.add_int(0)
        message.add_int(0)
        message.send(self.__can)

    def send_message_2(self) -> None:
        """
        Sends:
            Bytes 0, 1 - State of charge
            Bytes 2, 3 - State of health
            Bytes 4, 5 - State of charge * 10
            Bytes 6, 7 - 0
        """
        message = CanMessage(0x355)
        message.add_int(int(self.__bms.state_of_charge))
        message.add_int(100)
        message.add_int(int(self.__bms.state_of_charge * 10))
        message.send(self.__can)

    def send_message_3(self) -> None:
        """
        Sends:
            Bytes 0, 1 - Pack voltage (mV)
            Bytes 2, 3 - Current / 100
            Bytes 4, 5 - Average temperature (0.1)
            Bytes 6, 7 - 0

        msg.buf[0] = lowByte(uint16_t(bms.getPackVoltage() * 100));
        msg.buf[1] = highByte(uint16_t(bms.getPackVoltage() * 100));
        msg.buf[2] = lowByte(long(currentact / 100));
        msg.buf[3] = highByte(long(currentact / 100));
        msg.buf[4] = lowByte(int16_t(bms.getAvgTemperature() * 10));
        msg.buf[5] = highByte(int16_t(bms.getAvgTemperature() * 10));
        """
        message = CanMessage(0x356)
        message.add_int(int(self.__bms.battery_pack.voltage * 100))
        message.add_int(0)
        message.add_int(int(self.__bms.battery_pack.average_temperature * 10))
        message.send(self.__can)

    def send_message_4(self) -> None:
        """
        Sends:
            Bytes 0, 1, 2, 3 - Alarms
            Bytes 4, 5, 6, 7 - Warnings
        """
        message = CanMessage(0x35A)

        alarms = [0, 0, 0, 0]
        if self.__bms.battery_pack.alarms is not None:
            if OVER_VOLTAGE in self.__bms.battery_pack.alarms:
                alarms[0] = alarms[0] | 0x04
            if UNDER_VOLTAGE in self.__bms.battery_pack.alarms:
                alarms[0] = alarms[0] | 0x10
            if OVER_TEMPERATURE in self.__bms.battery_pack.alarms:
                alarms[0] = alarms[0] | 0x40
            if UNDER_TEMPERATURE in self.__bms.battery_pack.alarms:
                alarms[1] = alarms[1] | 0x01
            if BALANCE in self.__bms.battery_pack.alarms:
                alarms[3] = alarms[3] | 0x01
        message.add_byte(alarms[0])
        message.add_byte(alarms[1])
        message.add_byte(alarms[2])
        message.add_byte(alarms[3])

        warnings = [0, 0, 0, 0]
        if self.__bms.battery_pack.warnings is not None:
            if OVER_VOLTAGE in self.__bms.battery_pack.warnings:
                warnings[0] = warnings[0] | 0x04
            if UNDER_VOLTAGE in self.__bms.battery_pack.warnings:
                warnings[0] = warnings[0] | 0x10
            if OVER_TEMPERATURE in self.__bms.battery_pack.warnings:
                warnings[0] = warnings[0] | 0x40
            if UNDER_TEMPERATURE in self.__bms.battery_pack.warnings:
                warnings[1] = warnings[1] | 0x01
            if BALANCE in self.__bms.battery_pack.warnings:
                warnings[3] = warnings[3] | 0x01
        message.add_byte(warnings[0])
        message.add_byte(warnings[1])
        message.add_byte(warnings[2])
        message.add_byte(warnings[3])
        message.send(self.__can)

    def send_message_5(self) -> None:
        message = CanMessage(0x35E)
        message.add_string("pyBms   ")
        message.send(self.__can)

    def send_message_6(self) -> None:
        message = CanMessage(0x370)
        message.add_string("pyBms   ")
        message.send(self.__can)

    def send_message_7(self) -> None:
        """
        Sends:
            Bytes 0, 1 - Lowest cell voltage (mV)
            Bytes 2, 3 - Highest cell voltage (mV)
            Bytes 4, 5 - Low temperature (K)
            Bytes 4, 5 - High temperature (K)
            Bytes 6, 7 - 0
        """
        message = CanMessage(0x373)
        message.add_int(int(self.__bms.battery_pack.low_cell_voltage * 1000))
        message.add_int(int(self.__bms.battery_pack.high_cell_voltage * 1000))
        message.add_int(int(self.__bms.battery_pack.low_temperature + 273.15))
        message.add_int(int(self.__bms.battery_pack.high_temperature + 273.15))
        message.send(self.__can)

    def send_message_8(self) -> None:
        """
        Sends:
            Bytes 0, 1    - Battery Pack Capacity
            Bytes 2       - Contactor state
            Bytes 3       - Outputs
            Bytes 4       - BMS status
            Bytes 5, 6, 7 - 0

        msg.buf[0] = lowByte(uint16_t(settings.Pstrings * settings.CAP));
        msg.buf[1] = highByte(uint16_t(settings.Pstrings * settings.CAP));
        msg.buf[2] = contstat; //contactor state
        msg.buf[3] = (digitalRead(OUT1) | (digitalRead(OUT2) << 1) | (digitalRead(OUT3) << 2) | (digitalRead(OUT4) << 3));
        msg.buf[4] = bmsstatus;
        """
        message = CanMessage(0x379)
        message.add_int(int(self.__bms.battery_pack.capacity))
        message.add_byte(0)
        message.add_byte(0)
        message.add_byte(0)
        message.send(self.__can)

    def send_message_9(self) -> None:
        """
        Sends:
            Bytes 0, 1 - Number of modules
        """
        message = CanMessage(0x372)
        message.add_int(len(self.__bms.battery_pack.modules))
        message.send(self.__can)
