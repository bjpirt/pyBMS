from bms import Bms
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from hal.contactor_gpio.HardwareContactorGpio import HardwareContactorGpio
from machine import Pin, UART


def main():
    uart = UART(0, 612500, tx=Pin(0), rx=Pin(1))
    uart.init(timeout=5, timeout_char=5)
    contactors = HardwareContactorGpio(4, 5, 6)
    gateway = TeslaModelSNetworkGateway(uart, debug=True)
    pack = TeslaModelSBatteryPack(1, gateway)
    bms = Bms(pack, contactors, debug=True)

    while True:
        bms.process()


main()
