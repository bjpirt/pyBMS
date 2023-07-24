try:
    from machine import Pin as Pin
except ModuleNotFoundError:
    from .dummy_pin import DummyPin as Pin
