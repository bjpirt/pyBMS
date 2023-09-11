from bms import Bms, VictronOutput, Network, C2TTransducer
from config import Config
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from machine import UART  # type: ignore
from esp32 import CAN  # type: ignore


def main():
    uart = UART(1, 612500, tx=13, rx=15)
    can = CAN(0, CAN.LOOPBACK, baudrate=500_000, tx=5, rx=23)
    uart.init(timeout=5, timeout_char=5)
    config = Config()
    gateway = TeslaModelSNetworkGateway(uart, config)
    pack = TeslaModelSBatteryPack(gateway, config)
    current_sensor = C2TTransducer(config, sda_pin=19, sck_pin=18)
    bms = Bms(pack, config, current_sensor)
    victronOutput = VictronOutput(can, bms, 0.5)
    Network(bms, config)

    while True:
        bms.process()
        victronOutput.process()


main()
