from battery import BatteryPack
from battery.Constants import *
from hal.interval import get_interval


class CanMessage:
    def __init__(self, id: int) -> None:
        self.__id: int = id
        self.__message = bytearray()

    def addInt(self, value: int) -> None:
        self.__message.append(value & 0xFF)
        self.__message.append((value >> 8) & 0xFF)

    def addByte(self, value: int) -> None:
        self.__message.append(value & 0xFF)

    def addString(self, value: str) -> None:
        self.__message.extend(map(ord, value))

    def send(self, can) -> None:
        for _ in range(8 - len(self.__message)):
            self.__message.append(0)
        can.send(self.__message, self.__id)


class VictronOutput:
    def __init__(self, can, pack: BatteryPack, interval: float) -> None:
        self.__can = can
        self.__pack = pack
        self.__interval = get_interval()
        self.__interval.set(interval)

    def process(self):
        if self.__interval.ready and self.__pack.ready:
            self.send()
            self.__interval.reset()

    def send(self) -> None:
        self.sendMessage1()
        self.sendMessage2()
        self.sendMessage3()
        self.sendMessage4()
        self.sendMessage5()
        self.sendMessage6()
        self.sendMessage7()
        self.sendMessage8()
        self.sendMessage9()

    def sendMessage1(self) -> None:
        """
        Sends:
            Bytes 0, 1 - settings.StoreVsetpoint * settings.Scells ??
            Bytes 2, 3 - Charge current
            Bytes 4, 5 - Discharge current
            Bytes 6, 7 - DischVsetpoint * settings.Scells ??
        """
        message = CanMessage(0x351)
        message.addInt(0)
        message.addInt(0)
        message.addInt(0)
        message.addInt(0)
        message.send(self.__can)
        """
        msg.buf[0] = lowByte(uint16_t((settings.StoreVsetpoint * settings.Scells ) * 10));
        msg.buf[1] = highByte(uint16_t((settings.StoreVsetpoint * settings.Scells ) * 10));
        msg.buf[2] = lowByte(chargecurrent);
        msg.buf[3] = highByte(chargecurrent);
        msg.buf[4] = lowByte(discurrent );
        msg.buf[5] = highByte(discurrent);
        msg.buf[6] = lowByte(uint16_t((settings.DischVsetpoint * settings.Scells) * 10));
        msg.buf[7] = highByte(uint16_t((settings.DischVsetpoint * settings.Scells) * 10));
        Can0.write(msg);
        """

    def sendMessage2(self) -> None:
        """
        Sends:
            Bytes 0, 1 - State of charge
            Bytes 2, 3 - State of health
            Bytes 4, 5 - State of charge * 10
            Bytes 6, 7 - 0
        """
        message = CanMessage(0x355)
        message.addInt(0)
        message.addInt(100)
        message.addInt(0)
        message.send(self.__can)
        """
        msg.buf[0] = lowByte(SOC);
        msg.buf[1] = highByte(SOC);
        msg.buf[2] = lowByte(SOH);
        msg.buf[3] = highByte(SOH);
        msg.buf[4] = lowByte(SOC * 10);
        msg.buf[5] = highByte(SOC * 10);
        msg.buf[6] = 0;
        msg.buf[7] = 0;
        Can0.write(msg);
        """

    def sendMessage3(self) -> None:
        """
        Sends:
            Bytes 0, 1 - Pack voltage (mV)
            Bytes 2, 3 - Current / 100
            Bytes 4, 5 - Average temperature (0.1)
            Bytes 6, 7 - 0
        """
        message = CanMessage(0x356)
        message.addInt(int(self.__pack.voltage * 100))
        message.addInt(0)
        message.addInt(int(self.__pack.averageTemperature * 10))
        message.send(self.__can)
        """
        msg.buf[0] = lowByte(uint16_t(bms.getPackVoltage() * 100));
        msg.buf[1] = highByte(uint16_t(bms.getPackVoltage() * 100));
        msg.buf[2] = lowByte(long(currentact / 100));
        msg.buf[3] = highByte(long(currentact / 100));
        msg.buf[4] = lowByte(int16_t(bms.getAvgTemperature() * 10));
        msg.buf[5] = highByte(int16_t(bms.getAvgTemperature() * 10));
        msg.buf[6] = 0;
        msg.buf[7] = 0;
        Can0.write(msg);
        """

    def sendMessage4(self) -> None:
        """
        Sends:
            Bytes 0, 1, 2, 3 - Alarms
            Bytes 4, 5, 6, 7 - Warnings
        """
        message = CanMessage(0x35A)

        alarms = [0, 0, 0, 0]
        if self.__pack.alarms != None:
            if OVER_VOLTAGE_ALARM in self.__pack.alarms:
                alarms[0] = alarms[0] | 0x04
            if UNDER_VOLTAGE_ALARM in self.__pack.alarms:
                alarms[0] = alarms[0] | 0x10
            if OVER_TEMPERATURE_ALARM in self.__pack.alarms:
                alarms[0] = alarms[0] | 0x40
            if UNDER_TEMPERATURE_ALARM in self.__pack.alarms:
                alarms[1] = alarms[1] | 0x01
            if BALANCE_ALARM in self.__pack.alarms:
                alarms[3] = alarms[3] | 0x01
        message.addByte(alarms[0])
        message.addByte(alarms[1])
        message.addByte(alarms[2])
        message.addByte(alarms[3])

        warnings = [0, 0, 0, 0]
        if self.__pack.warnings != None:
            if OVER_VOLTAGE_ALARM in self.__pack.warnings:
                warnings[0] = warnings[0] | 0x04
            if UNDER_VOLTAGE_ALARM in self.__pack.warnings:
                warnings[0] = warnings[0] | 0x10
            if OVER_TEMPERATURE_ALARM in self.__pack.warnings:
                warnings[0] = warnings[0] | 0x40
            if UNDER_TEMPERATURE_ALARM in self.__pack.warnings:
                warnings[1] = warnings[1] | 0x01
            if BALANCE_ALARM in self.__pack.warnings:
                warnings[3] = warnings[3] | 0x01
        message.addByte(warnings[0])
        message.addByte(warnings[1])
        message.addByte(warnings[2])
        message.addByte(warnings[3])
        message.send(self.__can)

    def sendMessage5(self) -> None:
        message = CanMessage(0x35E)
        message.addString("pyBms   ")
        message.send(self.__can)

    def sendMessage6(self) -> None:
        message = CanMessage(0x370)
        message.addString("pyBms   ")
        message.send(self.__can)

    def sendMessage7(self) -> None:
        """
        Sends:
            Bytes 0, 1 - Lowest cell voltage (mV)
            Bytes 2, 3 - Highest cell voltage (mV)
            Bytes 4, 5 - Low temperature (K)
            Bytes 4, 5 - High temperature (K)
            Bytes 6, 7 - 0
        """
        message = CanMessage(0x373)
        message.addInt(int(self.__pack.lowCellVoltage * 1000))
        message.addInt(int(self.__pack.highCellVoltage * 1000))
        message.addInt(int(self.__pack.lowTemperature + 273.15))
        message.addInt(int(self.__pack.highTemperature + 273.15))
        message.send(self.__can)

    def sendMessage8(self) -> None:
        """
        Sends:
            Bytes 0, 1    - Battery Pack Capacity
            Bytes 2       - Contactor state
            Bytes 3       - Outputs
            Bytes 4       - BMS status
            Bytes 5, 6, 7 - 0
        """
        message = CanMessage(0x379)
        message.addInt(int(self.__pack.capacity))
        message.addByte(0)
        message.addByte(0)
        message.addByte(0)
        message.send(self.__can)
        """
        msg.buf[0] = lowByte(uint16_t(settings.Pstrings * settings.CAP));
        msg.buf[1] = highByte(uint16_t(settings.Pstrings * settings.CAP));
        msg.buf[2] = contstat; //contactor state
        msg.buf[3] = (digitalRead(OUT1) | (digitalRead(OUT2) << 1) | (digitalRead(OUT3) << 2) | (digitalRead(OUT4) << 3));
        msg.buf[4] = bmsstatus;
        """

    def sendMessage9(self) -> None:
        """
        Sends:
            Bytes 0, 1 - Number of modules
        """
        message = CanMessage(0x372)
        message.addInt(len(self.__pack.modules))
        message.send(self.__can)
