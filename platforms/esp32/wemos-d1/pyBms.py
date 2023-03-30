from bms import Bms, Config, VictronOutput, WebServer
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from hal.contactor_gpio.hardware_contactor_gpio import HardwareContactorGpio
from machine import UART  # type: ignore
from esp32 import CAN  # type: ignore


def main():
    uart = UART(1, 612500, tx=10, rx=9)
    can = CAN(0, CAN.NORMAL, baudrate=500_000, tx=21, rx=22)
    uart.init(timeout=5, timeout_char=5)
    config = Config()
    contactors = HardwareContactorGpio(
        config.negative_pin, config.precharge_pin, config.positive_pin)
    gateway = TeslaModelSNetworkGateway(uart, config)
    pack = TeslaModelSBatteryPack(gateway, config)
    bms = Bms(pack, contactors, config)
    victronOutput = VictronOutput(can, bms, 0.5)
    WebServer(bms, config)

    while True:
        bms.process()
        victronOutput.process()


# main()
