from bms import Bms, Config
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from hal.contactor_gpio.hardware_contactor_gpio import HardwareContactorGpio
from machine import Pin, UART  # type: ignore


def main():
    uart = UART(0, 612500, tx=Pin(0), rx=Pin(1))
    uart.init(timeout=5, timeout_char=5)
    config = Config()
    contactors = HardwareContactorGpio(
        config.negative_pin, config.precharge_pin, config.positive_pin)
    gateway = TeslaModelSNetworkGateway(uart, debug=config.debug)
    pack = TeslaModelSBatteryPack(gateway, config)
    bms = Bms(pack, contactors, debug=config.debug)

    while True:
        bms.process()


main()
