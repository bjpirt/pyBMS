from hal.interval import get_interval
from hal.pin import Pin


class Led:
    def __init__(self, led_pin: int, frequency: float = 1, duration: float = 0.05):
        self.__led = Pin(led_pin, Pin.OUT)
        self.__led_on: bool = False
        self.__frequency = frequency
        self.__duration = duration
        self.__led_interval = get_interval()
        self.__led_interval.set(frequency)

    def off(self):
        self.__led.off()

    def on(self):
        self.__led.on()

    def process(self):
        if self.__led_interval.ready:
            if self.__led_on:
                self.off()
                self.__led_on = False
                self.__led_interval.set(self.__frequency - self.__duration)
            else:
                self.on()
                self.__led_on = True
                self.__led_interval.set(self.__duration)
