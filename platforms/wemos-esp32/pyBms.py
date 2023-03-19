from bms import Bms, VictronOutput
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from hal.contactor_gpio.HardwareContactorGpio import HardwareContactorGpio
from machine import UART
from esp32 import CAN


def main():
    uart = UART(0, 612500, tx=1, rx=3)
    can = CAN(0, CAN.NORMAL, baudrate=500_000, tx=21, rx=22)
    uart.init(timeout=5, timeout_char=5)
    contactors = HardwareContactorGpio(4, 5, 6)
    gateway = TeslaModelSNetworkGateway(uart, debug=True)
    pack = TeslaModelSBatteryPack(1, gateway)
    bms = Bms(pack, contactors, debug=True)
    victronOutput = VictronOutput(can, pack, 0.5)

    while True:
        bms.process()
        victronOutput.process()


main()
