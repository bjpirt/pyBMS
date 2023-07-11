from bms import Bms, Config, VictronOutput, WebServer
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from machine import UART  # type: ignore
from esp32 import CAN  # type: ignore


def main():
    uart = UART(1, 612500, tx=13, rx=15)
    can = CAN(0, CAN.NORMAL, baudrate=500_000, tx=5, rx=23)
    uart.init(timeout=5, timeout_char=5)
    config = Config()
    gateway = TeslaModelSNetworkGateway(uart, config)
    pack = TeslaModelSBatteryPack(gateway, config)
    bms = Bms(pack, config)
    victronOutput = VictronOutput(can, bms, 0.5)
    WebServer(bms, config)

    while True:
        bms.process()
        victronOutput.process()


main()
