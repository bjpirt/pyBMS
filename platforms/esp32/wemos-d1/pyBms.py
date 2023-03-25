from bms import Bms, Config, VictronOutput
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from hal.contactor_gpio.HardwareContactorGpio import HardwareContactorGpio
from machine import UART
from esp32 import CAN


def main():
    uart = UART(0, 612500, tx=1, rx=3)
    can = CAN(0, CAN.NORMAL, baudrate=500_000, tx=21, rx=22)
    uart.init(timeout=5, timeout_char=5)
    config = Config()
    contactors = HardwareContactorGpio(
        config.negativePin, config.prechargePin, config.positivePin)
    gateway = TeslaModelSNetworkGateway(uart, debug=config.debug)
    pack = TeslaModelSBatteryPack(gateway, config)
    bms = Bms(pack, contactors, config)
    victronOutput = VictronOutput(can, bms, 0.5)

    while True:
        bms.process()
        victronOutput.process()


main()
