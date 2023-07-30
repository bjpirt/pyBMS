import random
from machine import Pin, UART  # type: ignore

from emulator.tesla_bms import TeslaBmsEmulator
from hal.interval import get_interval


def main():
    led = Pin(2, Pin.OUT)
    uart = UART(0, 612500, tx=1, rx=3)
    uart.init(timeout=5, timeout_char=5)
    interval = get_interval()
    interval.set(1)

    bms = TeslaBmsEmulator(uart, debug_interval=1, debug_comms=True)
    while True:
        moduleVoltage = 0.0
        for id in range(6):
            cellVoltage = 3.6 + random.random()/2
            bms.set_cell_voltage(id, cellVoltage)
            moduleVoltage = moduleVoltage + cellVoltage
        bms.set_module_voltage(moduleVoltage)
        bms.process()
        if interval.ready:
            led.value(not led.value())
            interval.set(1)


main()
