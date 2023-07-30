try:
    from machine import I2C as I2C # type: ignore
except ModuleNotFoundError:
    from .dummy_i2c import I2C as I2C
