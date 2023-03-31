from __future__ import annotations
from hal.interval import get_interval
from typing import TYPE_CHECKING
from hal import Pin
if TYPE_CHECKING:
    from .config import Config


class ContactorState():
    """
    States

    DISABLED - all contactors are off
    NEGATIVE_ON - only the negative contactor is on
    PRECHARGE_ON - the negative and precharge contactors are on
    ALL_ON - all contactors are on
    ENABLED - positive and negative contactors are on, precharge is off
    """
    DISABLED = "DISABLED"
    NEGATIVE_ON = "NEGATIVE_ON"
    PRECHARGE_ON = "PRECHARGE_ON"
    ALL_ON = "ALL_ON"
    ENABLED = "ENABLED"


class ContactorControl:
    def __init__(self, config: Config):
        self.__config = config
        self.__state = ContactorState.DISABLED
        self.__desired_state = ContactorState.DISABLED
        self.__interval = get_interval()
        self.__negative_pin = Pin(self.__config.negative_pin, Pin.OUT)
        self.__precharge_pin = Pin(self.__config.precharge_pin, Pin.OUT)
        self.__positive_pin = Pin(self.__config.positive_pin, Pin.OUT)

    @property
    def state(self):
        return self.__state

    def enable(self):
        self.__desired_state = ContactorState.ENABLED

    def disable(self):
        self.__desired_state = ContactorState.DISABLED

    def process(self):
        if self.__desired_state == ContactorState.DISABLED:
            self.__state = ContactorState.DISABLED

        if self.__state != self.__desired_state:
            if self.__state == ContactorState.DISABLED:
                self.__state = ContactorState.NEGATIVE_ON
                self.__interval.set(self.__config.contactor_negative_time)
            elif self.__state == ContactorState.NEGATIVE_ON:
                if self.__interval.ready:
                    self.__state = ContactorState.PRECHARGE_ON
                    self.__interval.set(self.__config.contactor_precharge_time)
            elif self.__state == ContactorState.PRECHARGE_ON:
                if self.__interval.ready:
                    self.__state = ContactorState.ALL_ON
                    self.__interval.set(self.__config.contactor_precharge_time)
            elif self.__state == ContactorState.ALL_ON:
                if self.__interval.ready:
                    self.__state = ContactorState.ENABLED
        self.__control()

    def __control(self):
        if self.__state == ContactorState.DISABLED:
            self.__negative_pin.value(False)
            self.__precharge_pin.value(False)
            self.__positive_pin.value(False)
        elif self.__state == ContactorState.NEGATIVE_ON:
            self.__negative_pin.value(True)
            self.__precharge_pin.value(False)
            self.__positive_pin.value(False)
        elif self.__state == ContactorState.PRECHARGE_ON:
            self.__negative_pin.value(True)
            self.__precharge_pin.value(True)
            self.__positive_pin.value(False)
        elif self.__state == ContactorState.ALL_ON:
            self.__negative_pin.value(True)
            self.__precharge_pin.value(True)
            self.__positive_pin.value(True)
        elif self.__state == ContactorState.ENABLED:
            self.__negative_pin.value(True)
            self.__precharge_pin.value(False)
            self.__positive_pin.value(True)

    def get_dict(self):
        return {
            "state": self.__state
        }
