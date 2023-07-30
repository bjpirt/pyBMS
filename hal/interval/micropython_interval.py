import time
from .interval import Interval


class MicroPythonInterval(Interval):
    # pylint: disable=E1101
    def __init__(self) -> None:
        self.__ready_time: int = -1
        self.__last_interval: float

    def set(self, interval: float) -> None:
        self.__ready_time = time.ticks_add(  # type: ignore
            time.ticks_ms(), int(interval * 1000))  # type: ignore
        self.__last_interval = interval

    def reset(self) -> None:
        self.set(self.__last_interval)

    @property
    def ready(self) -> bool:
        return time.ticks_diff(self.__ready_time, time.ticks_ms()) <= 0  # type: ignore
