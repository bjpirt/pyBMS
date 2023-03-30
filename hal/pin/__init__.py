try:
    from machine import Pin  # type: ignore
except:
    from .dummy_pin import DummyPin as Pin
