import os
import sys
import serial
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from bms import Bms  # nopep8
from hal import DummyContactorGpio  # nopep8
from battery.tesla_model_s import TeslaModelSBatteryPack, TeslaModelSNetworkGateway  # nopep8

port = sys.argv[1]
baud = int(sys.argv[2])

serialPort = serial.Serial(port, baud, timeout=0.1)
contactors = DummyContactorGpio()
gateway = TeslaModelSNetworkGateway(serialPort)
pack = TeslaModelSBatteryPack(1, gateway)
bms = Bms(pack, contactors, debug=True)


def main():
    while True:
        bms.process()


if __name__ == '__main__':
    main()
