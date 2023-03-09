import random
import serial
import sys
from os import path  # type: ignore

sys.path.insert(0, path.join(path.dirname(__file__), "../.."))

from emulator.tesla_bms import TeslaBmsEmulator  # nopep8

port = sys.argv[1]
baud = int(sys.argv[2])

serialPort = serial.Serial(port, baud, timeout=0.1)

bms = TeslaBmsEmulator(serialPort)


def main():
    while True:
        moduleVoltage = 0
        for id in range(6):
            cellVoltage = 3.6 + random.random()/2
            bms.setCellVoltage(id, cellVoltage)
            moduleVoltage = moduleVoltage + cellVoltage
        bms.setModuleVoltage(moduleVoltage)
        bms.process()


if __name__ == '__main__':
    main()
