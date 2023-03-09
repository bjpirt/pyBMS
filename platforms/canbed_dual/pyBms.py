from bms import Bms
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from hal.contactor_gpio.HardwareContactorGpio import HardwareContactorGpio
from machine import Pin, UART


uart = UART(0, 612500, tx=Pin(0), rx=Pin(1))
contactors = HardwareContactorGpio(4, 5, 6)
gateway = TeslaModelSNetworkGateway(uart)
pack = TeslaModelSBatteryPack(1, gateway)
bms = Bms(pack, contactors, debug=True)


def main():
    while True:
        bms.process()


if __name__ == '__main__':
    main()
