import os
import json


def exists(filename: str) -> bool:
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


class Config:
    def __init__(self, file="config.json"):
        self.__file = file
        # Initialise the defaults
        # The number of modules in the pack
        self.module_count: int = 2
        # The number of parallel strings of modules in the pack
        self.parallel_string_count: int = 1
        # The high voltage setpoint for the cells
        self.cell_high_voltage_setpoint: float = 4.1
        # The low voltage setpoint for the cells
        self.cell_low_voltage_setpoint: float = 3.6
        # The high temperature setpoint
        self.high_temperature_setpoint: float = 65.0
        # The low temperature setpoint
        self.low_temperature_setpoint: float = 5.0
        # The number of seconds without communication before raising an alarm
        self.comms_timeout: float = 10.0
        # The pin number for the negative contactor
        self.negative_pin: int = 16
        # The pin number for the precharge contactor
        self.precharge_pin: int = 17
        # The pin number for the positive contactor
        self.positive_pin: int = 26
        # Whether to print debug information over serial
        self.debug: bool = False
        # Whether to print debug comms information over serial
        self.debugComms: bool = False
        # Whether the BMS should balance the modules automatically
        self.auto_balance: bool = True
        # How long to balance the cells for in seconds
        self.balance_time: int = 5
        # The voltage above which balancing should be enabled
        self.balance_voltage: float = 3.9
        # The difference between a module's highest and lowest cell voltages that triggers balancing
        self.balance_difference: float = 0.04
        # The capacity of an individual module in Ah
        self.module_capacity: float = 232.0
        # The maximum allowed difference in cell voltages
        self.max_cell_voltage_difference: float = 0.2
        # The offset from the max and min charge voltages that triggers a warning
        self.voltage_warning_offset: float = 0.1
        # The offset from the max and min charge voltages that will cause the BMS hardware to raise a fault
        self.voltage_hardware_offset: float = 0.05
        # The offset from the max and min temperatures that triggers a warning
        self.temperature_warning_offset: float = 5.0
        # The offset from the max and min cell voltage differences that triggers a warning
        self.voltage_difference_warning_offset: float = 0.05
        # The interval between queries to the BMS in seconds
        self.poll_interval: float = 0.5
        # The pin to use for the LED
        self.led_pin = 18
        # The voltage to state of charge lookup table
        self.soc_lookup = [
            [3.0, 0.0],
            [3.1, 0.1],
            [4.1, 0.9],
            [4.2, 1.0]
        ]
        # The wifi network to connect to
        self.wifi_network: str = ""
        # The wifi network password
        self.wifi_password: str = ""
        # The amount of time for the negative contactor to be on before turning on the precharge
        self.contactor_negative_time: float = 1
        # The amount of time for the precharge contactor to be on before turning on the positive contactor
        self.contactor_precharge_time: float = 5.0
        # Use the hardware fault detection built in to the Tesla BMS modules
        self.hardware_fault_detection = False

        self.read()

    def get_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_Config__")}

    def read(self):
        data = None
        if exists(self.__file):
            with open(self.__file, 'r', encoding="UTF-8") as file:
                data = file.read()
        else:
            try:
                import config_json  # type: ignore
                data = config_json.data().tobytes()
            except:
                pass
        if data:
            new_config = json.loads(data)
            self.update(new_config)

    def update(self, new_config: dict) -> None:
        for (key, value) in new_config.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def save(self):
        with open(self.__file, 'w') as file:
            json.dump(self.get_dict(), file)
