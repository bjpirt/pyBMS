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

    def test_voltage_fault(self):
        self.assertEqual(self.cell.voltageFault, False)
        self.cell.overVoltageFault = True
        self.assertEqual(self.cell.voltageFault, True)
        self.cell.overVoltageFault = False
        self.cell.underVoltageFault = True
        self.assertEqual(self.cell.voltageFault, True)
