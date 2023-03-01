from enum import Enum
import time

from hal import ContactorGpio

"""
States

DISABLED - all contactors are off
NEGATIVE_ON - only the negative contactor is on
PRECHARGE_ON - the negative and precharge contactors are on
ENABLED - all contactors are on
"""

ContactorState: Enum = Enum('ContactorState', ['DISABLED', 'NEGATIVE_ON', 'PRECHARGE_ON', 'ENABLED'])

class ContactorControl:
    def __init__(self, contactorGpio: ContactorGpio, negativeTime = 1, prechargeTime = 5):
        self.__contactorGpio = contactorGpio
        self.__state: ContactorState = ContactorState.DISABLED
        self.__desiredState = ContactorState.DISABLED
        self.__negativeTime = negativeTime
        self.__prechargeTime = prechargeTime
        self.__timer = time.time()
    
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
            match self.__state:
                case ContactorState.DISABLED:
                    self.__state = ContactorState.NEGATIVE_ON
                    self.__timer = time.time()
                case ContactorState.NEGATIVE_ON:
                    if time.time() > self.__timer + self.__negativeTime:
                        self.__state = ContactorState.PRECHARGE_ON
                        self.__timer = time.time()
                case ContactorState.PRECHARGE_ON:
                    if time.time() > self.__timer + self.__prechargeTime:
                        self.__state = ContactorState.ENABLED
        self.__control()

    def __control(self):
        match self.__state:
            case ContactorState.DISABLED:
                self.__contactorGpio.update(negative=False, precharge=False, positive=False)
            case ContactorState.NEGATIVE_ON:
                self.__contactorGpio.update(negative=True, precharge=False, positive=False)
            case ContactorState.PRECHARGE_ON:
                self.__contactorGpio.update(negative=True, precharge=True, positive=False)
            case ContactorState.ENABLED:
                self.__contactorGpio.update(negative=True, precharge=True, positive=True)
