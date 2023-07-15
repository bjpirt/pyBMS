from battery import BatteryCell
import unittest
from battery.constants import OVER_VOLTAGE, UNDER_VOLTAGE

from bms import Config


class BatteryCellTestCase(unittest.TestCase):
    def setUp(self):
        c = Config("config.default.json")
        self.cell = BatteryCell(c)

    def test_store_highest_voltage(self):
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.voltage, 3.0)
        self.assertEqual(self.cell.highest_voltage, 3.0)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.voltage, 2.9)
        self.assertEqual(self.cell.highest_voltage, 3.0)
        self.cell.voltage = 3.1
        self.assertEqual(self.cell.voltage, 3.1)
        self.assertEqual(self.cell.highest_voltage, 3.1)

    def test_store_lowest_voltage(self):
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.voltage, 3.0)
        self.assertEqual(self.cell.lowest_voltage, 3.0)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.voltage, 2.9)
        self.assertEqual(self.cell.lowest_voltage, 2.9)
        self.cell.voltage = 3.1
        self.assertEqual(self.cell.voltage, 3.1)
        self.assertEqual(self.cell.lowest_voltage, 2.9)

    def test_over_voltage_fault(self):
        self.cell.voltage = 5.0
        self.assertTrue(self.cell.over_voltage_fault)

    def test_over_voltage_alert(self):
        self.cell.voltage = 4.05
        self.assertTrue(self.cell.over_voltage_alert)

    def test_under_voltage_fault(self):
        self.cell.voltage = 3.5
        self.assertTrue(self.cell.under_voltage_fault)

    def test_under_voltage_alert(self):
        self.cell.voltage = 3.65
        self.assertTrue(self.cell.under_voltage_alert)

    def test_fault(self):
        self.cell.voltage = 4.0
        self.assertFalse(self.cell.fault)
        self.cell.voltage = 3.0
        self.assertTrue(self.cell.fault)
        self.cell.voltage = 5.0
        self.assertTrue(self.cell.fault)

    def test_faults(self):
        self.cell.voltage = 4.0
        self.assertEqual(self.cell.faults, [])
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.faults, [UNDER_VOLTAGE])
        self.cell.voltage = 5.0
        self.assertEqual(self.cell.faults, [OVER_VOLTAGE])

    def test_alerts(self):
        self.cell.voltage = 3.9
        self.assertEqual(self.cell.alerts, [])
        self.cell.voltage = 3.65
        self.assertEqual(self.cell.alerts, [UNDER_VOLTAGE])
        self.cell.voltage = 4.05
        self.assertEqual(self.cell.alerts, [OVER_VOLTAGE])
