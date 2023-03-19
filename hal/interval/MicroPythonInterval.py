import time
from .Interval import Interval


class MicroPythonInterval(Interval):
    def __init__(self) -> None:
        self.__readyTime: int = -1

    def set(self, interval: float) -> None:
        self.__readyTime = time.ticks_add(
            time.ticks_ms(), int(interval * 1000))
        self.__lastInterval = interval

    def reset(self) -> None:
        self.set(self.__lastInterval)

    @property
    def ready(self) -> bool:
        return time.ticks_diff(self.__readyTime, time.ticks_ms()) <= 0
