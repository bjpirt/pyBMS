class LowPassFilter():
    def __init__(self, factor) -> None:
        self.__factor = factor
        self.__previous: float
    
    def process(self, new_value: float) -> float:
        try:
            self.__previous = (self.__previous * self.__factor) + (new_value * (1 - self.__factor))
        except AttributeError:
            self.__previous = new_value
        return self.__previous
