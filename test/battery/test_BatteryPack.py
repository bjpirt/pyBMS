from battery import BatteryCell, BatteryModule, BatteryPack
import unittest
from battery.constants import COMMS, OVER_VOLTAGE, OVER_TEMPERATURE, UNDER_VOLTAGE, UNDER_TEMPERATURE, BALANCE
from bms import Config


class BatteryPackTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Config("config.default.json")
        self.config.parallel_string_count = 2
        self.pack = BatteryPack(self.config)
        for m in range(4):
            module = BatteryModule(self.config)
            for i in range(4):
                cell = BatteryCell(self.config)
                cell.voltage = 3.8
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
        self.assertEqual(self.pack.low_cell_voltage, 3.8)
        self.pack.modules[0].cells[0].voltage = 3.6
        self.assertEqual(self.pack.low_cell_voltage, 3.6)

    def test_high_cell_voltage(self):
        self.assertEqual(self.pack.high_cell_voltage, 3.8)
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

    def test_fault(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 4.0
        self.pack.modules[0].cells[0].voltage = 3.0
        self.assertTrue(self.pack.fault)
        self.pack.modules[0].cells[0].voltage = 5.0
        self.assertTrue(self.pack.fault)
        self.pack.modules[0].cells[0].voltage = 4.0
        self.assertFalse(self.pack.fault)
        self.pack.modules[0].temperatures[0] = 66
        self.assertTrue(self.pack.fault)

    def test_capacity(self):
        self.assertEqual(self.pack.capacity, 232)

    def test_no_faults(self):
        self.assertEqual(self.pack.faults, [])

    def test_over_temperature_faults(self):
        self.pack.modules[0].temperatures = [66, 66]
        self.assertEqual(self.pack.faults, [OVER_TEMPERATURE])
        self.assertTrue(self.pack.fault)

    def test_under_temperature_faults(self):
        self.pack.modules[0].temperatures = [9, 9]
        self.assertEqual(self.pack.faults, [UNDER_TEMPERATURE])
        self.assertTrue(self.pack.fault)

    def test_over_voltage_faults(self):
        for cell in self.pack.modules[0].cells:
            cell.voltage = 4.1
        self.pack.modules[0].cells[1].voltage = 4.15
        self.pack.modules[0].cells[2].voltage = 4.15
        self.pack.modules[0].cells[3].voltage = 4.15
        self.assertEqual(self.pack.faults, [OVER_VOLTAGE])
        self.assertTrue(self.pack.fault)

    def test_under_voltage_faults(self):
        for cell in self.pack.modules[0].cells:
            cell.voltage = 3.4
        self.pack.modules[0].cells[1].voltage = 3.35
        self.pack.modules[0].cells[2].voltage = 3.35
        self.pack.modules[0].cells[3].voltage = 3.35
        self.assertEqual(self.pack.faults, [UNDER_VOLTAGE])
        self.assertTrue(self.pack.fault)

    def test_comms_faults(self):
        self.pack.modules[0].comms_fault = True
        self.assertEqual(self.pack.faults, [COMMS])
        self.assertTrue(self.pack.fault)

    def test_balance_faults(self):
        self.pack.modules[0].cells[0].voltage = 4.01
        self.assertEqual(self.pack.faults, [BALANCE])
        self.assertTrue(self.pack.fault)

    def test_no_alerts(self):
        self.assertEqual(self.pack.alerts, [])

    def test_over_temperature_alerts(self):
        self.pack.modules[0].temperatures = [61, 61]
        self.assertEqual(self.pack.alerts, [OVER_TEMPERATURE])
        self.assertTrue(self.pack.alert)

    def test_under_temperature_alerts(self):
        self.pack.modules[0].temperatures = [12, 12]
        self.assertEqual(self.pack.alerts, [UNDER_TEMPERATURE])
        self.assertTrue(self.pack.alert)

    def test_over_voltage_alerts(self):
        for cell in self.pack.modules[0].cells:
            cell.voltage = 4.1
        self.pack.modules[0].cells[3].voltage = 4.125
        self.assertEqual(self.pack.alerts, [OVER_VOLTAGE])
        self.assertTrue(self.pack.alert)

    def test_under_voltage_alerts(self):
        for module in self.pack.modules:
            for cell in module.cells:
                cell.voltage = 3.6

        self.pack.modules[0].cells[3].voltage = 3.575
        self.assertEqual(self.pack.alerts, [UNDER_VOLTAGE])
        self.assertTrue(self.pack.alert)

    def test_balance_alerts(self):
        self.pack.modules[0].cells[0].voltage = 3.975
        self.assertEqual(self.pack.alerts, [BALANCE])
        self.assertTrue(self.pack.alert)
