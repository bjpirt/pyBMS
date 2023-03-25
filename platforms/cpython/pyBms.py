import sys
import serial
from os import path  # type: ignore

sys.path.insert(0, path.join(path.dirname(__file__), "../.."))

from bms import Bms, Config  # nopep8
from hal import DummyContactorGpio  # nopep8
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway  # nopep8

port = sys.argv[1]
baud = int(sys.argv[2])

serialPort = serial.Serial(port, baud, timeout=0.1)
contactors = DummyContactorGpio()
config = Config()
gateway = TeslaModelSNetworkGateway(serialPort, debug=config.debug)
pack = TeslaModelSBatteryPack(gateway, config)
bms = Bms(pack, contactors, config)


def main():
    while True:
        bms.process()


if __name__ == '__main__':
    main()
