from battery.BatteryCell import BatteryCell
from battery.BatteryModule import BatteryModule
import unittest


class BatteryModuleTestCase(unittest.TestCase):
    def setUp(self):
        self.module = BatteryModule()
        for i in range(4):
            cell = BatteryCell()
            cell.voltage = i + 1
            self.module.cells.append(cell)
        self.module.voltage = 24.0
        self.module.temperatures.append(20.0)
        self.module.temperatures.append(22.0)
        self.module.update()

    def test_average_cell_voltage(self):
        self.assertEqual(self.module.averageCellVoltage, 2.5)

    def test_low_cell_voltage(self):
        self.assertEqual(self.module.lowCellVoltage, 1.0)

    def test_high_cell_voltage(self):
        self.assertEqual(self.module.highCellVoltage, 4.0)

    def test_lowest_cell_voltage(self):
        self.assertEqual(self.module.lowestCellVoltage, 1.0)
        self.module.cells[0].voltage = 0.9
        self.module.update()
        self.assertEqual(self.module.lowestCellVoltage, 0.9)

    def test_highest_cell_voltage(self):
        self.assertEqual(self.module.highestCellVoltage, 4.0)
        self.module.cells[3].voltage = 4.1
        self.module.update()
        self.assertEqual(self.module.highestCellVoltage, 4.1)

    def test_lowest_module_voltage(self):
        self.assertEqual(self.module.lowestVoltage, 24.0)
        self.module.voltage = 22.0
        self.module.update()
        self.assertEqual(self.module.lowestVoltage, 22.0)

    def test_highest_module_voltage(self):
        self.assertEqual(self.module.highestVoltage, 24.0)
        self.module.voltage = 26.0
        self.module.update()
        self.assertEqual(self.module.highestVoltage, 26.0)

    def test_average_temperature(self):
        self.assertEqual(self.module.averageTemperature, 21.0)

    def test_low_temperature(self):
        self.assertEqual(self.module.lowTemperature, 20.0)

    def test_high_temperature(self):
        self.assertEqual(self.module.highTemperature, 22.0)

    def test_lowest_temperature(self):
        self.assertEqual(self.module.lowestTemperature, 20.0)
        self.module.temperatures[0] = 18.0
        self.module.update()
        self.assertEqual(self.module.lowestTemperature, 18.0)

    def test_highest_temperature(self):
        self.assertEqual(self.module.highestTemperature, 22.0)
        self.module.temperatures[1] = 24.0
        self.module.update()
        self.assertEqual(self.module.highestTemperature, 24.0)
