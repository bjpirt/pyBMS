import random
import time
from machine import Pin, UART

from emulator.tesla_bms import TeslaBmsEmulator


uart = UART(0, 612500, tx=Pin(0), rx=Pin(1))
uart.init(timeout=100, timeout_char=100)

bms = TeslaBmsEmulator(uart, debugInterval=1, debugComms=True)


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
