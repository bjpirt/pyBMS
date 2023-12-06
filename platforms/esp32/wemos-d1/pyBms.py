from bms import Bms, VictronOutput, Network, C2TTransducer
from config import Config
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway
from machine import UART  # type: ignore
from bms.battery_heating import BatteryHeating
from esp32 import CAN  # type: ignore


def main():
    uart = UART(1, 612500, tx=33, rx=32)
    can = CAN(0, CAN.LOOPBACK, baudrate=500_000, tx=5, rx=17)
    uart.init(timeout=5, timeout_char=5)
    config = Config()
    gateway = TeslaModelSNetworkGateway(uart, config)
    pack = TeslaModelSBatteryPack(gateway, config)
    current_sensor = C2TTransducer(config, sda_pin=14, sck_pin=15)
    bms = Bms(pack, config, current_sensor)
    Network(bms, config)
    victron_output = VictronOutput(can, bms, 0.5)
    heating_control = BatteryHeating(config, pack)

    while True:
        bms.process()
        victron_output.process()
        heating_control.process()


main()
