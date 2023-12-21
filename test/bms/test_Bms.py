import unittest
from battery.battery_pack import BatteryPack  # type: ignore
from config import Config
from bms.bms import Bms
from bms.current_sensor.current_sensor import CurrentSensor


class FakeCurrentSensor(CurrentSensor):
    def __init__(self) -> None:
        self.fake_current = 10.0

    @property
    def current(self):
        return self.fake_current


class FakePack(BatteryPack):
    def __init__(self):
        self.fake_high_cell_voltage = 3.9
        self.ready = True

    @property
    def high_cell_voltage(self):
        return self.fake_high_cell_voltage


class BmsTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.pack = FakePack()
        self.current_sensor = FakeCurrentSensor()
        self.bms = Bms(self.pack, self.config, self.current_sensor)
        return super().setUp()

    def test_charge_current_setpoint_under_voltage(self):
        self.assertEqual(self.bms.charge_current_setpoint, 100)

    def test_charge_current_setpoint_over_voltage(self):
        self.pack.fake_high_cell_voltage = 4.35
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 5)
        self.pack.fake_high_cell_voltage = 4.2
        self.current_sensor.fake_current = 5
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 3.16666667)
        self.pack.fake_high_cell_voltage = 4.12
        self.current_sensor.fake_current = 3.16
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 2.844)
        self.pack.fake_high_cell_voltage = 4.09
        self.current_sensor.fake_current = 2.844
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 2.844)
        self.pack.fake_high_cell_voltage = 4.1
        self.current_sensor.fake_current = 2.844
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 2.844)
        self.pack.fake_high_cell_voltage = 4.11
        self.current_sensor.fake_current = 2.844
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 2.5596)
        self.pack.fake_high_cell_voltage = 4.1
        self.current_sensor.fake_current = 2.5596
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 2.5596)
        self.pack.fake_high_cell_voltage = 4.04
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 2.81556)
        self.pack.fake_high_cell_voltage = 4.05
        self.current_sensor.fake_current = 2.81556
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 3.097116)
        self.pack.fake_high_cell_voltage = 4.09
        self.current_sensor.fake_current = 2.81556
        self.assertAlmostEqual(self.bms.charge_current_setpoint, 3.097116)
