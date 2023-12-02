from battery.battery_pack import BatteryPack
from bms.config import Config
from hal import Pin


class BatteryHeating:
    def __init__(self, config: Config, pack: BatteryPack) -> None:
        self.set_temperature = config.battery_heating_temperature
        self.__pack = pack
        self.__pin = Pin(config.battery_heating_pin, Pin.OUT)
        self.heating = False

    def process(self):
        if self.__pack.low_temperature < self.set_temperature:
            self.__pin.on()

        if self.__pack.low_temperature > self.set_temperature + 1:
            self.__pin.off()
