import time
from .Interval import Interval


class CPythonInterval(Interval):
    def __init__(self) -> None:
        self.__readyTime: float = -1.0

    def set(self, interval: float) -> None:
        self.__readyTime = time.time() + interval

    @property
    def ready(self) -> bool:
        return self.__readyTime != -1.0 and time.time() > self.__readyTime
