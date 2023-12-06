from battery.battery_pack import BatteryPack
from config import Config
from hal import Pin


class BatteryHeating:
    def __init__(self, config: Config, pack: BatteryPack) -> None:
        self.__config = config
        self.__pack = pack
        self.__pin = Pin(config.battery_heating_pin, Pin.OUT)
        self.heating = False

    def process(self):
        if self.__pack.low_temperature < self.__config.battery_heating_temperature:
            self.__pin.on()

        if self.__pack.low_temperature > self.__config.battery_heating_temperature + 1:
            self.__pin.off()
