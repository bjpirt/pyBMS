from .CPythonInterval import CPythonInterval
from .MicroPythonInterval import MicroPythonInterval
from .Interval import Interval

upy = True
try:
    import machine
except:
    upy = False


def get_interval() -> Interval:
    if upy:
        return MicroPythonInterval()
    else:
        return CPythonInterval()
