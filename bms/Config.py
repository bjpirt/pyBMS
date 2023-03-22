from os import path  # type: ignore
import json


class Config:
    def __init__(self, file="config.json"):
        self.__file = file
        # Initialise the defaults
        # The number of modules in the pack
        self.moduleCount: int = 2
        # The number of parallel strings of modules in the pack
        self.parallelStringCount: int = 1
        # The high voltage setpoint for the cells
        self.cellHighVoltageSetpoint: float = 4.1
        # The low voltage setpoint for the cells
        self.cellLowVoltageSetpoint: float = 3.6
        # The high temperature setpoint
        self.highTemperatureSetpoint: float = 65.0
        # The low temperature setpoint
        self.lowTemperatureSetpoint: float = 10.0
        # The number of seconds without communication before raising an alarm
        self.commsTimeout: float = 10.0
        # The pin number for the negative contactor
        self.negativePin: int = 4
        # The pin number for the precharge contactor
        self.prechargePin: int = 5
        # The pin number for the positive contactor
        self.positivePin: int = 6
        # Whether to print debug information over serial
        self.debug: bool = False
        # Whether the BMS should balance the modules automatically
        self.autoBalance: bool = True
        # How long to balance the cells for in seconds
        self.balanceTime: int = 5
        # The voltage above which balancing should be enabled
        self.balanceVoltage: float = 3.9
        # The difference between a module's highest and lowest cell voltages that triggers balancing
        self.balanceDifference: float = 0.4

        self.readConfig()

    def __getDict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_Config__")}

    def readConfig(self):
        data = None
        if path.exists(self.__file):
            with open(self.__file, 'r') as fp:
                data = fp.read()
        else:
            try:
                import config_json
                data = config_json.data().tobytes()
            except:
                pass
        if data:
            newConfig = json.loads(data)
            self.applyConfig(newConfig)

    def applyConfig(self, newConfig: dict) -> None:
        for (k, v) in newConfig.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def saveConfig(self):
        with open(self.__file, 'w') as fp:
            json.dump(self.__getDict(), fp)
