from machine import Pin  # type: ignore
from .contactor_gpio import ContactorGpio


class HardwareContactorGpio(ContactorGpio):
    def __init__(self, negative_pin: int, precharge_pin: int, positive_pin: int):
        self.__negative_pin = Pin(negative_pin, Pin.OUT)
        self.__precharge_pin = Pin(precharge_pin, Pin.OUT)
        self.__positive_pin = Pin(positive_pin, Pin.OUT)

    def update(self, negative: bool, precharge: bool, positive: bool):
        self.__negative_pin.value(int(negative))
        self.__precharge_pin.value(int(precharge))
        self.__positive_pin.value(int(positive))
