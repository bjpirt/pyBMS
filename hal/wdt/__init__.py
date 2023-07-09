try:
    from machine import WDT  # type: ignore
except:
    from .dummy_wdt import DummyWDT as WDT
