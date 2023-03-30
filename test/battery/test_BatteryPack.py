from battery import BatteryCell, BatteryModule, BatteryPack
import unittest
from battery.constants import *
from bms import Config


class BatteryPackTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.config.parallel_string_count = 2
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
        self.assertEqual(self.pack.low_cell_voltage, 1.0)
        self.pack.modules[0].cells[0].voltage = 0.9
        self.assertEqual(self.pack.low_cell_voltage, 0.9)

    def test_high_cell_voltage(self):
        self.assertEqual(self.pack.high_cell_voltage, 4.0)
        self.pack.modules[0].cells[0].voltage = 4.1
        self.assertEqual(self.pack.high_cell_voltage, 4.1)

    def test_highest_voltage(self):
        self.assertEqual(self.pack.highest_voltage, 48.0)
        self.pack.modules[0].voltage = 25.0
        self.pack.update()
        self.assertEqual(self.pack.highest_voltage, 48.5)

    def test_lowest_voltage(self):
        self.assertEqual(self.pack.lowest_voltage, 48.0)
        self.pack.modules[0].voltage = 23.0
        self.pack.update()
        self.assertEqual(self.pack.lowest_voltage, 47.5)

    def test_average_temperature(self):
        self.assertEqual(self.pack.average_temperature, 21.0)

    def test_low_temperature(self):
        self.assertEqual(self.pack.low_temperature, 20.0)

    def test_high_temperature(self):
        self.assertEqual(self.pack.high_temperature, 22.0)

    def test_lowest_temperature(self):
        self.assertEqual(self.pack.lowest_temperature, 20.0)
        self.pack.modules[0].temperatures[0] = 18.0
        self.pack.update()
        self.assertEqual(self.pack.lowest_temperature, 18.0)

    def test_highest_temperature(self):
        self.assertEqual(self.pack.highest_temperature, 22.0)
        self.pack.modules[0].temperatures[0] = 24.0
        self.pack.update()
        self.assertEqual(self.pack.highest_temperature, 24.0)

    def test_has_fault(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 4.0
        self.pack.modules[0].cells[0].voltage = 3.0
        self.assertTrue(self.pack.has_fault)
        self.pack.modules[0].cells[0].voltage = 5.0
        self.assertTrue(self.pack.has_fault)
        self.pack.modules[0].cells[0].voltage = 4.0
        self.assertFalse(self.pack.has_fault)
        self.pack.modules[0].temperatures[0] = 66
        self.assertTrue(self.pack.has_fault)

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
                cell.voltage = self.config.cell_high_voltage_setpoint + 0.01
        self.assertEqual(self.pack.alarms, [OVER_VOLTAGE])

    def test_under_voltage_alarm(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = self.config.cell_low_voltage_setpoint - 0.01
        self.assertEqual(self.pack.alarms, [UNDER_VOLTAGE])

    def test_over_temperature_alarm(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.9
            module.temperatures[0] = self.config.high_temperature_setpoint + 0.01
        self.assertEqual(self.pack.alarms, [OVER_TEMPERATURE])

    def test_under_temperature_alarm(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.9
            module.temperatures[0] = self.config.low_temperature_setpoint - 0.01
        self.assertEqual(self.pack.alarms, [UNDER_TEMPERATURE])

    def test_balance_alarm(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.8
        self.pack.modules[0].cells[0].voltage = 4.01
        self.assertEqual(self.pack.alarms, [BALANCE])

    def test_over_voltage_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = self.config.cell_high_voltage_setpoint - \
                    self.config.voltage_warning_offset + 0.01
        print(self.pack.cell_voltage_difference)
        self.assertEqual(self.pack.warnings, [OVER_VOLTAGE])

    def test_under_voltage_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = self.config.cell_low_voltage_setpoint + \
                    self.config.voltage_warning_offset - 0.01
        self.assertEqual(self.pack.warnings, [UNDER_VOLTAGE])

    def test_over_temperature_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.9
            module.temperatures[0] = self.config.high_temperature_setpoint - \
                self.config.temperature_warning_offset + 0.01
        self.assertEqual(self.pack.warnings, [OVER_TEMPERATURE])

    def test_under_temperature_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.9
            module.temperatures[0] = self.config.low_temperature_setpoint + \
                self.config.temperature_warning_offset - 0.01
        self.assertEqual(self.pack.warnings, [UNDER_TEMPERATURE])

    def test_balance_warning(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.8
        self.pack.modules[0].cells[0].voltage = 3.8 - self.config.voltage_difference_warning_offset + \
            self.config.max_cell_voltage_difference + 0.01
        self.assertEqual(self.pack.warnings, [BALANCE])
