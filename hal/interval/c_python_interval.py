import time
from .interval import Interval


class CPythonInterval(Interval):
    def __init__(self) -> None:
        self.__ready_time: float = -1.0
        self.__last_interval: float

    def set(self, interval: float) -> None:
        self.__ready_time = time.time() + interval
        self.__last_interval = interval

    def reset(self) -> None:
        self.set(self.__last_interval)

    @property
    def ready(self) -> bool:
        return self.__ready_time != -1.0 and time.time() > self.__ready_time
