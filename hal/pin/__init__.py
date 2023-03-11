try:
    from machine import Pin
except:
    from .DummyPin import DummyPin as Pin
