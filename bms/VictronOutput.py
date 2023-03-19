from battery import BatteryPack
from hal.interval import get_interval


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
        id = 0x351
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
        id = 0x355
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
        id = 0x356
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
        id = 0x35A
        """
        msg.buf[0] = alarm[0];//High temp  Low Voltage | High Voltage
        msg.buf[1] = alarm[1]; // High Discharge Current | Low Temperature
        msg.buf[2] = alarm[2]; //Internal Failure | High Charge current
        msg.buf[3] = alarm[3];// Cell Imbalance
        msg.buf[4] = warning[0];//High temp  Low Voltage | High Voltage
        msg.buf[5] = warning[1];// High Discharge Current | Low Temperature
        msg.buf[6] = warning[2];//Internal Failure | High Charge current
        msg.buf[7] = warning[3];// Cell Imbalance
        Can0.write(msg);
        """

    def sendMessage5(self) -> None:
        id = 0x35E
        message = "pyBms   "
        self.__can.send(id, message)

    def sendMessage6(self) -> None:
        id = 0x370
        message = "pyBms   "
        self.__can.send(id, message)

    def sendMessage7(self) -> None:
        id = 0x373
        """
        msg.buf[0] = lowByte(uint16_t(bms.getLowCellVolt() * 1000));
        msg.buf[1] = highByte(uint16_t(bms.getLowCellVolt() * 1000));
        msg.buf[2] = lowByte(uint16_t(bms.getHighCellVolt() * 1000));
        msg.buf[3] = highByte(uint16_t(bms.getHighCellVolt() * 1000));
        msg.buf[4] = lowByte(uint16_t(bms.getLowTemperature() + 273.15));
        msg.buf[5] = highByte(uint16_t(bms.getLowTemperature() + 273.15));
        msg.buf[6] = lowByte(uint16_t(bms.getHighTemperature() + 273.15));
        msg.buf[7] = highByte(uint16_t(bms.getHighTemperature() + 273.15));
        Can0.write(msg);
        """

    def sendMessage8(self) -> None:
        id = 0x379
        """
        msg.buf[0] = lowByte(uint16_t(settings.Pstrings * settings.CAP));
        msg.buf[1] = highByte(uint16_t(settings.Pstrings * settings.CAP));
        msg.buf[2] = contstat; //contactor state
        msg.buf[3] = (digitalRead(OUT1) | (digitalRead(OUT2) << 1) | (digitalRead(OUT3) << 2) | (digitalRead(OUT4) << 3));
        msg.buf[4] = bmsstatus;
        msg.buf[5] = 0x00;
        msg.buf[6] = 0x00;
        msg.buf[7] = 0x00;
        Can0.write(msg);
        """

    def sendMessage9(self) -> None:
        id = 0x372
        """
        msg.buf[0] = lowByte(bms.getNumModules());
        msg.buf[1] = highByte(bms.getNumModules());
        msg.buf[2] = 0x00;
        msg.buf[3] = 0x00;
        msg.buf[4] = 0x00;
        msg.buf[5] = 0x00;
        msg.buf[6] = 0x00;
        msg.buf[7] = 0x00;
        Can0.write(msg);
        """
