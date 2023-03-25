import unittest
from battery import BatteryPack
from bms import Config, StateOfCharge


class FakeConfig(Config):
    def __init__(self):
        self.socLookup = [
            [3.0, 0.0],
            [3.1, 0.1],
            [4.1, 0.9],
            [4.2, 1.0]
        ]
        self.cellHighVoltageSetpoint = 4.0
        self.cellLowVoltageSetpoint = 3.2


class FakePack(BatteryPack):
    def __init__(self):
        self.fakeAverageCellVoltage = 3.6

    @property
    def averageCellVoltage(self):
        return self.fakeAverageCellVoltage


class StateOfChargeTestCase(unittest.TestCase):
    def setUp(self):
        self.config = FakeConfig()
        self.pack = FakePack()
        self.soc = StateOfCharge(self.pack, self.config)
        return super().setUp()

    def test_calculate_from_voltage(self):
        self.assertAlmostEqual(self.soc.level, 0.5)
        self.pack.fakeAverageCellVoltage = 3.7
        self.assertAlmostEqual(self.soc.level, 0.58)

    def test_scaled_level(self):
        self.assertAlmostEqual(self.soc.scaledLevel, 0.5)
        self.pack.fakeAverageCellVoltage = 3.7
        self.assertAlmostEqual(self.soc.scaledLevel, 0.625)
