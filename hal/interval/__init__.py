from .c_python_interval import CPythonInterval
from .micropython_interval import MicroPythonInterval
from .interval import Interval

MPY = True
try:
    import machine  # type: ignore
except:
    MPY = False


def get_interval() -> Interval:
    if MPY:
        return MicroPythonInterval()
    return CPythonInterval()
