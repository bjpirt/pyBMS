try:
    from machine import reset as reset  # type: ignore
except ModuleNotFoundError:
    from .dummy_machine import reset as reset
