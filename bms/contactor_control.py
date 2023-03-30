from hal import ContactorGpio
from hal.interval import get_interval


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
    def __init__(self,
                 contactor_gpio: ContactorGpio,
                 negative_time: float = 1,
                 precharge_time: float = 5):
        self.__contactor_gpio = contactor_gpio
        self.__state = ContactorState.DISABLED
        self.__desired_state = ContactorState.DISABLED
        self.__negative_time = negative_time
        self.__precharge_time = precharge_time
        self.__interval = get_interval()

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
                self.__interval.set(self.__negative_time)
            elif self.__state == ContactorState.NEGATIVE_ON:
                if self.__interval.ready:
                    self.__state = ContactorState.PRECHARGE_ON
                    self.__interval.set(self.__precharge_time)
            elif self.__state == ContactorState.PRECHARGE_ON:
                if self.__interval.ready:
                    self.__state = ContactorState.ALL_ON
                    self.__interval.set(self.__precharge_time)
            elif self.__state == ContactorState.ALL_ON:
                if self.__interval.ready:
                    self.__state = ContactorState.ENABLED
        self.__control()

    def __control(self):
        if self.__state == ContactorState.DISABLED:
            self.__contactor_gpio.update(
                negative=False, precharge=False, positive=False)
        elif self.__state == ContactorState.NEGATIVE_ON:
            self.__contactor_gpio.update(
                negative=True, precharge=False, positive=False)
        elif self.__state == ContactorState.PRECHARGE_ON:
            self.__contactor_gpio.update(
                negative=True, precharge=True, positive=False)
        elif self.__state == ContactorState.ALL_ON:
            self.__contactor_gpio.update(
                negative=True, precharge=True, positive=True)
        elif self.__state == ContactorState.ENABLED:
            self.__contactor_gpio.update(
                negative=True, precharge=False, positive=True)

    def get_dict(self):
        return {
            "state": self.__state
        }
