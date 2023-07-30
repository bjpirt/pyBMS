try:
    from machine import Pin as Pin # type: ignore
except ModuleNotFoundError:
    from .dummy_pin import DummyPin as Pin
