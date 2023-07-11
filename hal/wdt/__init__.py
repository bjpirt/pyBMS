try:
    from machine import WDT as WDT  # type: ignore
except ModuleNotFoundError:
    from .dummy_wdt import DummyWDT as WDT
