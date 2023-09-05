# ruff: noqa: E402
import random
import serial  # type: ignore
import sys
from os import path


sys.path.insert(0, path.join(path.dirname(__file__), "../.."))

from emulator.tesla_bms import TeslaBmsEmulator  # nopep8
from hal import get_interval  # type: ignore # nopep8

port = sys.argv[1]
baud = int(sys.argv[2])
serial_port = serial.Serial(port, baud, timeout=0.1)
bms = TeslaBmsEmulator(serial_port, debug_interval=1)

interval = get_interval()
interval.set(3)


def main():
    while True:
        if interval.ready:
            interval.reset()
            moduleVoltage = 0.0
            for id in range(6):
                cellVoltage = 3.6 + random.random()/2
                bms.set_cell_voltage(id, cellVoltage)
                moduleVoltage = moduleVoltage + cellVoltage
            bms.set_module_voltage(moduleVoltage)
        bms.process()


if __name__ == '__main__':
    main()
