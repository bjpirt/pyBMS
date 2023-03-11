from hal.interval import get_interval
from hal.pin import Pin


class Led:
    def __init__(self, ledPin: int, frequency: float = 1, duration: float = 0.05):
        self.__led = Pin(ledPin, Pin.OUT)
        self.__ledOn: bool = False
        self.__frequency = frequency
        self.__duration = duration
        self.__ledInterval = get_interval()
        self.__ledInterval.set(frequency)

    def off(self):
        self.__led.off()

    def on(self):
        self.__led.on()

    def process(self):
        if self.__ledInterval.ready:
            if self.__ledOn:
                self.off()
                self.__ledOn = False
                self.__ledInterval.set(self.__frequency - self.__duration)
            else:
                self.on()
                self.__ledOn = True
                self.__ledInterval.set(self.__duration)
