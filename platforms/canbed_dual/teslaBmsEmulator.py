import random
from machine import Pin, UART

from emulator.tesla_bms import TeslaBmsEmulator


uart = UART(0, 612500, tx=Pin(0), rx=Pin(1))

bms = TeslaBmsEmulator(uart)


def main():
    while True:
        moduleVoltage = 0
        for id in range(6):
            cellVoltage = 3.6 + random.random()/2
            bms.setCellVoltage(id, cellVoltage)
            moduleVoltage = moduleVoltage + cellVoltage
        bms.setModuleVoltage(moduleVoltage)
        bms.process()


main()
