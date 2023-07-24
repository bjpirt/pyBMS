from ..config import Config
from .mcp3421 import MCP3421
from .current_sensor import CurrentSensor

class C2TTransducer(CurrentSensor):
    def __init__(self, config: Config, sda_pin: int, sck_pin: int) -> None:
        self.__ratio: float = config.current_zero_point / 5.0
        self.__adc = MCP3421(sda_pin, sck_pin)
        self.__max_current = 200.0
        self.__current = 0.0
  
    def read(self) -> float:
        if not self.__adc.ready:
            raise RuntimeError("ADC is not ready")
        
        rawVoltage = self.__adc.read()
        scaledVoltage = rawVoltage / self.__ratio
        self.__current = ((scaledVoltage - 5.0) / 2.0) * self.__max_current
        return self.__current
    
    @property
    def current(self)-> float:
        return self.__current
