from .CPythonInterval import CPythonInterval
from .MicroPythonInterval import MicroPythonInterval
from .Interval import Interval

upy = False
try:
    import machine
    upy = True
except:
    pass


def get_interval() -> Interval:
    if upy:
        return MicroPythonInterval()
    else:
        return CPythonInterval()
