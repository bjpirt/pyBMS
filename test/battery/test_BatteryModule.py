from battery.battery_cell import BatteryCell
from battery.battery_module import BatteryModule
import unittest

from bms import Config


class BatteryModuleTestCase(unittest.TestCase):
    def setUp(self):
        c = Config()
        self.module = BatteryModule(c)
        for i in range(4):
            cell = BatteryCell(c)
            cell.voltage = i + 1
            self.module.cells.append(cell)
        self.module.voltage = 24.0
        self.module.temperatures.append(20.0)
        self.module.temperatures.append(22.0)
        self.module.update()

    def test_average_cell_voltage(self):
        self.assertEqual(self.module.average_cell_voltage, 2.5)

    def test_low_cell_voltage(self):
        self.assertEqual(self.module.low_cell_voltage, 1.0)

    def test_high_cell_voltage(self):
        self.assertEqual(self.module.high_cell_voltage, 4.0)

    def test_lowest_cell_voltage(self):
        self.assertEqual(self.module.lowest_cell_voltage, 1.0)
        self.module.cells[0].voltage = 0.9
        self.module.update()
        self.assertEqual(self.module.lowest_cell_voltage, 0.9)

    def test_highest_cell_voltage(self):
        self.assertEqual(self.module.highest_cell_voltage, 4.0)
        self.module.cells[3].voltage = 4.1
        self.module.update()
        self.assertEqual(self.module.highest_cell_voltage, 4.1)

    def test_lowest_module_voltage(self):
        self.assertEqual(self.module.lowest_voltage, 24.0)
        self.module.voltage = 22.0
        self.assertEqual(self.module.lowest_voltage, 22.0)

    def test_highest_module_voltage(self):
        self.assertEqual(self.module.highest_voltage, 24.0)
        self.module.voltage = 26.0
        self.assertEqual(self.module.highest_voltage, 26.0)

    def test_average_temperature(self):
        self.assertEqual(self.module.average_temperature, 21.0)

    def test_low_temperature(self):
        self.assertEqual(self.module.low_temperature, 20.0)

    def test_high_temperature(self):
        self.assertEqual(self.module.high_temperature, 22.0)

    def test_lowest_temperature(self):
        self.assertEqual(self.module.lowest_temperature, 20.0)
        self.module.temperatures[0] = 18.0
        self.module.update()
        self.assertEqual(self.module.lowest_temperature, 18.0)

    def test_highest_temperature(self):
        self.assertEqual(self.module.highest_temperature, 22.0)
        self.module.temperatures[1] = 24.0
        self.module.update()
        self.assertEqual(self.module.highest_temperature, 24.0)

    def test_has_fault(self):
        for cell in self.module.cells:
            cell.voltage = 4.0
        self.module.cells[0].voltage = 3.0
        self.assertTrue(self.module.has_fault)
        self.module.cells[0].voltage = 5.0
        self.assertTrue(self.module.has_fault)
        self.module.cells[0].voltage = 4.0
        self.assertFalse(self.module.has_fault)
        self.module.temperatures[0] = 66
        self.assertTrue(self.module.has_fault)
