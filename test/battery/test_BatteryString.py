import unittest
from battery import BatteryCell
from battery.battery_module import BatteryModule
from battery.battery_string import BatteryString
from config import Config


class TeslaModelSBatteryModuleTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.config.balance_difference = 0.1
        self.config.balancing_enabled = True
        self.config.balance_voltage = 3.6
        self.config.balance_measuring_time = 0
        self.modules = [BatteryModule(self.config), BatteryModule(self.config)]
        for module in self.modules:
            for i in range(0, 6):
                cell = BatteryCell(self.config)
                module.cells.append(cell)
                cell.voltage = 3.8

        self.string = BatteryString(self.modules, self.config)
        return super().setUp()

    def test_balance(self):
        self.modules[0].cells[1].voltage = 4.0
        self.string.balance()
        self.assertTrue(self.modules[0].cells[1].balancing)

    def test_no_balance_below_threshold(self):
        self.config.balance_voltage = 4.01
        self.modules[0].cells[1].voltage = 4.0
        self.string.balance()
        self.assertFalse(self.modules[0].cells[1].balancing)

    def test_no_balance_within_difference(self):
        self.modules[0].cells[1].voltage = 3.899
        self.string.balance()
        self.assertFalse(self.modules[0].cells[1].balancing)

    def test_no_balance_if_disabled(self):
        self.modules[0].cells[1].voltage = 4.0
        self.config.balancing_enabled = False
        self.string.balance()
        self.assertFalse(self.modules[0].cells[1].balancing)
