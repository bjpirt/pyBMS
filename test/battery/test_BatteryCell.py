from battery.BatteryCell import BatteryCell
import unittest


class BatteryCellTestCase(unittest.TestCase):
    def setUp(self):
        self.cell = BatteryCell()

    def test_store_highest_voltage(self):
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.voltage, 3.0)
        self.assertEqual(self.cell.highestVoltage, 3.0)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.voltage, 2.9)
        self.assertEqual(self.cell.highestVoltage, 3.0)
        self.cell.voltage = 3.1
        self.assertEqual(self.cell.voltage, 3.1)
        self.assertEqual(self.cell.highestVoltage, 3.1)

    def test_store_lowest_voltage(self):
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.voltage, 3.0)
        self.assertEqual(self.cell.lowestVoltage, 3.0)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.voltage, 2.9)
        self.assertEqual(self.cell.lowestVoltage, 2.9)
        self.cell.voltage = 3.1
        self.assertEqual(self.cell.voltage, 3.1)
        self.assertEqual(self.cell.lowestVoltage, 2.9)

    def test_over_voltage_fault(self):
        self.cell.overVoltageLevel = 4.5
        self.cell.voltage = 4.5
        self.assertEqual(self.cell.overVoltageFault, False)
        self.cell.voltage = 4.6
        self.assertEqual(self.cell.overVoltageFault, True)

    def test_under_voltage_fault(self):
        self.cell.underVoltageLevel = 3.0
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.underVoltageFault, False)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.underVoltageFault, True)

    def test_voltage_fault(self):
        self.cell.overVoltageLevel = 4.5
        self.cell.underVoltageLevel = 3.0
        self.cell.voltage = 3.4
        self.assertEqual(self.cell.voltageFault, False)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.voltageFault, True)
        self.cell.voltage = 4.6
        self.assertEqual(self.cell.voltageFault, True)
