from bms import Bms, Config
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from machine import Pin, UART  # type: ignore


def main():
    uart = UART(0, 612500, tx=Pin(0), rx=Pin(1))
    uart.init(timeout=5, timeout_char=5)
    config = Config()
    gateway = TeslaModelSNetworkGateway(uart, config)
    pack = TeslaModelSBatteryPack(gateway, config)
    bms = Bms(pack, config)

    while True:
        bms.process()


main()
