from machine import Pin
from .ContactorGpio import ContactorGpio


class HardwareContactorGpio(ContactorGpio):
    def __init__(self, negativePin: int, prechargePin: int, positivePin: int):
        self.__negativePin = Pin(negativePin, Pin.OUT)
        self.__prechargePin = Pin(prechargePin, Pin.OUT)
        self.__positivePin = Pin(positivePin, Pin.OUT)

    def update(self, negative: bool, precharge: bool, positive: bool):
        self.__negativePin.value(int(negative))
        self.__prechargePin.value(int(precharge))
        self.__positivePin.value(int(positive))
