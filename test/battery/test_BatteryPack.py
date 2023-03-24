from battery import BatteryCell, BatteryModule, BatteryPack
import unittest
from battery.Constants import *

from bms import Config


class BatteryPackTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.config.parallelStringCount = 2
        self.pack = BatteryPack(self.config)
        for m in range(4):
            module = BatteryModule(self.config)
            for i in range(4):
                cell = BatteryCell(self.config)
                cell.voltage = i + 1
                module.cells.append(cell)
            module.voltage = 24.0
            module.temperatures.append(20.0)
            module.temperatures.append(22.0)
            module.update()
            self.pack.modules.append(module)
        self.pack.update()

    def test_voltage(self):
        self.assertEqual(self.pack.voltage, 48.0)

    def test_low_cell_voltage(self):
        self.assertEqual(self.pack.lowCellVoltage, 1.0)
        self.pack.modules[0].cells[0].voltage = 0.9
        self.assertEqual(self.pack.lowCellVoltage, 0.9)

    def test_high_cell_voltage(self):
        self.assertEqual(self.pack.highCellVoltage, 4.0)
        self.pack.modules[0].cells[0].voltage = 4.1
        self.assertEqual(self.pack.highCellVoltage, 4.1)

    def test_highest_voltage(self):
        self.assertEqual(self.pack.highestVoltage, 48.0)
        self.pack.modules[0].voltage = 25.0
        self.pack.update()
        self.assertEqual(self.pack.highestVoltage, 48.5)

    def test_lowest_voltage(self):
        self.assertEqual(self.pack.lowestVoltage, 48.0)
        self.pack.modules[0].voltage = 23.0
        self.pack.update()
        self.assertEqual(self.pack.lowestVoltage, 47.5)

    def test_average_temperature(self):
        self.assertEqual(self.pack.averageTemperature, 21.0)

    def test_low_temperature(self):
        self.assertEqual(self.pack.lowTemperature, 20.0)

    def test_high_temperature(self):
        self.assertEqual(self.pack.highTemperature, 22.0)

    def test_lowest_temperature(self):
        self.assertEqual(self.pack.lowestTemperature, 20.0)
        self.pack.modules[0].temperatures[0] = 18.0
        self.pack.update()
        self.assertEqual(self.pack.lowestTemperature, 18.0)

    def test_highest_temperature(self):
        self.assertEqual(self.pack.highestTemperature, 22.0)
        self.pack.modules[0].temperatures[0] = 24.0
        self.pack.update()
        self.assertEqual(self.pack.highestTemperature, 24.0)

    def test_has_fault(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 4.0
        self.pack.modules[0].cells[0].voltage = 3.0
        self.assertTrue(self.pack.hasFault)
        self.pack.modules[0].cells[0].voltage = 5.0
        self.assertTrue(self.pack.hasFault)
        self.pack.modules[0].cells[0].voltage = 4.0
        self.assertFalse(self.pack.hasFault)
        self.pack.modules[0].temperatures[0] = 66
        self.assertTrue(self.pack.hasFault)

    def test_capacity(self):
        self.assertEqual(self.pack.capacity, 232)

    def test_no_alarms(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.9
        self.assertIsNone(self.pack.alarms)

    def test_over_voltage_alarm(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = self.config.cellHighVoltageSetpoint + 0.01
        self.assertEqual(self.pack.alarms, [OVER_VOLTAGE_ALARM])

    def test_under_voltage_alarm(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = self.config.cellLowVoltageSetpoint - 0.01
        self.assertEqual(self.pack.alarms, [UNDER_VOLTAGE_ALARM])

    def test_over_temperature_alarm(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.9
            module.temperatures[0] = self.config.highTemperatureSetpoint + 0.01
        self.assertEqual(self.pack.alarms, [OVER_TEMPERATURE_ALARM])

    def test_under_temperature_alarm(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.9
            module.temperatures[0] = self.config.lowTemperatureSetpoint - 0.01
        self.assertEqual(self.pack.alarms, [UNDER_TEMPERATURE_ALARM])

    def test_balance_alarm(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.8
        self.pack.modules[0].cells[0].voltage = 4.01
        self.assertEqual(self.pack.alarms, [BALANCE_ALARM])

    def test_over_voltage_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = self.config.cellHighVoltageSetpoint - \
                    self.config.voltageWarningOffset + 0.01
        print(self.pack.cellVoltageDifference)
        self.assertEqual(self.pack.warnings, [OVER_VOLTAGE_WARNING])

    def test_under_voltage_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = self.config.cellLowVoltageSetpoint + \
                    self.config.voltageWarningOffset - 0.01
        self.assertEqual(self.pack.warnings, [UNDER_VOLTAGE_WARNING])

    def test_over_temperature_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.9
            module.temperatures[0] = self.config.highTemperatureSetpoint - \
                self.config.temperatureWarningOffset + 0.01
        self.assertEqual(self.pack.warnings, [OVER_TEMPERATURE_WARNING])

    def test_under_temperature_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.9
            module.temperatures[0] = self.config.lowTemperatureSetpoint + \
                self.config.temperatureWarningOffset - 0.01
        self.assertEqual(self.pack.warnings, [UNDER_TEMPERATURE_WARNING])

    def test_balance_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.8
        self.pack.modules[0].cells[0].voltage = 3.8 - self.config.voltageDifferenceWarningOffset + \
            self.config.maxCellVoltageDifference + 0.01
        self.assertEqual(self.pack.warnings, [BALANCE_WARNING])
