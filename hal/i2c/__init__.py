try:
    from machine import I2C as I2C
except ModuleNotFoundError:
    from .dummy_i2c import I2C as I2C
