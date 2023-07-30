import unittest
from battery import BatteryPack
from bms import Config, StateOfCharge, CurrentSensor


class FakeConfig(Config):
    def __init__(self):
        self.soc_lookup = [
            [3.0, 0.0],
            [3.1, 0.1],
            [4.1, 0.9],
            [4.2, 1.0]
        ]
        self.cell_high_voltage_setpoint = 4.0
        self.cell_low_voltage_setpoint = 3.2
        self.module_capacity = 100
        self.parallel_string_count = 2


class FakePack(BatteryPack):
    def __init__(self):
        self.fakeaverage_cell_voltage = 3.6

    @property
    def average_cell_voltage(self):
        return self.fakeaverage_cell_voltage

class FakeCurrentSensor(CurrentSensor):
    pass


class StateOfChargeTestCase(unittest.TestCase):
    def setUp(self):
        self.config = FakeConfig()
        self.pack = FakePack()
        self.current_sensor = FakeCurrentSensor()
        self.soc = StateOfCharge(self.pack, self.current_sensor, self.config)
        return super().setUp()
    
    def test_initialise_current_soc_from_voltage(self):
        self.assertAlmostEqual(self.soc.level_from_current, 0.5)

    def test_level_from_voltage(self):
        self.pack.fakeaverage_cell_voltage = 3.7
        self.assertAlmostEqual(self.soc.level_from_voltage, 0.625)

    def test_level_from_voltage_at_minimum(self):
        self.pack.fakeaverage_cell_voltage = 3.0
        self.assertAlmostEqual(self.soc.level_from_voltage, 0.0)

    def test_level_from_voltage_below_minimum(self):
        self.pack.fakeaverage_cell_voltage = 2.9
        self.assertAlmostEqual(self.soc.level_from_voltage, 0.0)

    def test_level_from_voltage_at_maximum(self):
        self.pack.fakeaverage_cell_voltage = 4.2
        self.assertAlmostEqual(self.soc.level_from_voltage, 1.0)

    def test_level_from_voltage_above_maximum(self):
        self.pack.fakeaverage_cell_voltage = 4.3
        self.assertAlmostEqual(self.soc.level_from_voltage, 1.0)
