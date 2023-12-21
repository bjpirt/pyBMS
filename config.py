from lib import PersistentConfig
try:
    from initial_config import config   # type: ignore
except ImportError:
    config = {}


class Config (PersistentConfig):
    def __init__(self):
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
        self.low_temperature_setpoint: float = 10.0
        # The number of seconds without communication before raising an alarm
        self.comms_timeout: float = 10.0
        # Whether or not to control the contactors
        self.contactor_control_enabled = False
        # The pin number for the negative contactor
        self.negative_pin: int = 16
        # The pin number for the precharge contactor
        self.precharge_pin: int = 17
        # The pin number for the positive contactor
        self.positive_pin: int = 26
        # Whether to print debug information over serial
        self.debug: bool = False
        # Whether to print debug comms information over serial
        self.debug_comms: bool = False
        # Whether the BMS should balance the modules automatically
        self.balancing_enabled: bool = True
        # The voltage above which balancing should be enabled
        self.balance_voltage: float = 3.9
        # The difference between the voltage of a cell and the lowest cell voltage in the pack that triggers balancing
        self.balance_difference: float = 0.04
        # The capacity of an individual module in Ah
        self.module_capacity: float = 232.0
        # The maximum allowed difference in cell voltages
        self.max_cell_voltage_difference: float = 0.2
        # The offset from the max and min charge voltages that triggers an alert
        self.voltage_alert_offset: float = 0.025
        # The offset from the max and min charge voltages that triggers a fault
        self.voltage_fault_offset: float = 0.05
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
        # Watchdog timer time (0 to disable)
        self.wdt_timeout: int = 0
        # Use the hardware fault detection built in to the Tesla BMS modules
        self.hardware_fault_detection = False
        # The port to use for the web server
        self.web_server_port: int = 80
        # The zero-point reference voltage for the C2T current sensor
        self.current_zero_point: float = 1.6025
        # Whether to reverse the direction of the current sensor in software
        self.current_reversed: bool = False
        # The maximum amps for the full reading of the current sensor
        self.current_sensor_max: int = 200
        # The max desired charge current in A
        self.max_charge_current: float = 100.0
        # The max desired discharge current in A
        self.max_discharge_current: float = 100.0
        # The hysteresis offset voltage for enabling and disabling charging and discharging
        self.charge_hysteresis_voltage: float = 0.1
        # The hysteresis time (in seconds) for enabling and disabling charging and discharging
        self.charge_hysteresis_time: float = 30.0
        # The time spent measuring before balancing (seconds)
        self.balance_measuring_time: float = 2.0
        # The time spent balancing before checking the voltage again (seconds)
        self.balance_time: float = 10.0
        # The hysteresis time for over voltage faults in seconds
        self.over_voltage_hysteresis_time: float = 10.0
        # The temperature the battery heater should heat to
        self.battery_heating_temperature: float = 10.0
        # The pin to use for controlling the battery heating
        self.battery_heating_pin: int = 4
        # Use the current sensor for state of charge
        self.current_sensor_soc = False

        ######################################################################
        # MQTT Settings
        ######################################################################
        # Whether MQTT is enabled
        self.mqtt_enabled: bool = False
        # The host for the MQTT broker
        self.mqtt_host: str = ""
        # The host for the MQTT broker
        self.mqtt_topic_prefix: str = ""
        # The host for the MQTT broker
        self.mqtt_output_interval: float = 5.0
        # How long between sending a full update
        self.mqtt_full_output_interval: float = 120.0

        super().__init__(config)

    @property
    def high_voltage_alert_level(self):
        return self.cell_high_voltage_setpoint + self.voltage_alert_offset

    @property
    def high_voltage_fault_level(self):
        return self.cell_high_voltage_setpoint + self.voltage_fault_offset

    @property
    def low_voltage_alert_level(self):
        return self.cell_low_voltage_setpoint - self.voltage_alert_offset

    @property
    def low_voltage_fault_level(self):
        return self.cell_low_voltage_setpoint - self.voltage_fault_offset
