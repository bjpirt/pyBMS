# ruff: noqa: E402
import sys
import serial  # type: ignore
from os import path


sys.path.insert(0, path.join(path.dirname(__file__), "../.."))

from bms import Bms, Network  # nopep8
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway  # nopep8
from config import Config  # nopep8

port = sys.argv[1]
baud = int(sys.argv[2])

serialPort = serial.Serial(port, baud, timeout=0.1)
config = Config("config.local.json")
gateway = TeslaModelSNetworkGateway(serialPort, config)
pack = TeslaModelSBatteryPack(gateway, config)
bms = Bms(pack, config)
# webServer = WebServer(bms, config)
Network(bms, config)


def main():
    while True:
        bms.process()


if __name__ == '__main__':
    main()
