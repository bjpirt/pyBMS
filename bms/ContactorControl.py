from hal import ContactorGpio
from hal.interval import get_interval

"""
States

DISABLED - all contactors are off
NEGATIVE_ON - only the negative contactor is on
PRECHARGE_ON - the negative and precharge contactors are on
ALL_ON - all contactors are on
ENABLED - positive and negative contactors are on, precharge is off
"""


class ContactorState():
    DISABLED = "DISABLED"
    NEGATIVE_ON = "NEGATIVE_ON"
    PRECHARGE_ON = "PRECHARGE_ON"
    ALL_ON = "ALL_ON"
    ENABLED = "ENABLED"


class ContactorControl:
    def __init__(self, contactorGpio: ContactorGpio, negativeTime: float = 1, prechargeTime: float = 5):
        self.__contactorGpio = contactorGpio
        self.__state = ContactorState.DISABLED
        self.__desiredState = ContactorState.DISABLED
        self.__negativeTime = negativeTime
        self.__prechargeTime = prechargeTime
        self.__interval = get_interval()

    @property
    def state(self):
        return self.__state

    def enable(self):
        self.__desiredState = ContactorState.ENABLED

    def disable(self):
        self.__desiredState = ContactorState.DISABLED

    def process(self):
        if self.__desiredState == ContactorState.DISABLED:
            self.__state = ContactorState.DISABLED

        if self.__state != self.__desiredState:
            if self.__state == ContactorState.DISABLED:
                self.__state = ContactorState.NEGATIVE_ON
                self.__interval.set(self.__negativeTime)
            elif self.__state == ContactorState.NEGATIVE_ON:
                if self.__interval.ready:
                    self.__state = ContactorState.PRECHARGE_ON
                    self.__interval.set(self.__prechargeTime)
            elif self.__state == ContactorState.PRECHARGE_ON:
                if self.__interval.ready:
                    self.__state = ContactorState.ALL_ON
                    self.__interval.set(self.__prechargeTime)
            elif self.__state == ContactorState.ALL_ON:
                if self.__interval.ready:
                    self.__state = ContactorState.ENABLED
        self.__control()

    def __control(self):
        if self.__state == ContactorState.DISABLED:
            self.__contactorGpio.update(
                negative=False, precharge=False, positive=False)
        elif self.__state == ContactorState.NEGATIVE_ON:
            self.__contactorGpio.update(
                negative=True, precharge=False, positive=False)
        elif self.__state == ContactorState.PRECHARGE_ON:
            self.__contactorGpio.update(
                negative=True, precharge=True, positive=False)
        elif self.__state == ContactorState.ALL_ON:
            self.__contactorGpio.update(
                negative=True, precharge=True, positive=True)
        elif self.__state == ContactorState.ENABLED:
            self.__contactorGpio.update(
                negative=True, precharge=False, positive=True)

    def getDict(self):
        return {
            "state": self.__state
        }
