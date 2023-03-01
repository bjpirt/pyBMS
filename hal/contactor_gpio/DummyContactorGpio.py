from .ContactorGpio import ContactorGpio


class DummyContactorGpio(ContactorGpio):
    def __init__(self):
        self.__negativeContactor = False
        self.__positiveContactor = False
        self.__prechargeContactor = False
    
    def update(self, negative: bool, precharge: bool, positive: bool):
        self.__negativeContactor = negative
        self.__prechargeContactor = precharge
        self.__positiveContactor = positive
        self.__updateGpio()
    
    def __updateGpio(self):
        print(f"Contactor state: negative: {self.__negativeContactor} positive: {self.__positiveContactor} precharge: {self.__prechargeContactor}")
