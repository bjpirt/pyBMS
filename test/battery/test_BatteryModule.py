from battery.battery_cell import BatteryCell
from battery.battery_module import BatteryModule
import unittest
from battery.constants import COMMS, OVER_TEMPERATURE, OVER_VOLTAGE, UNDER_TEMPERATURE, UNDER_VOLTAGE
from time import sleep

from config import Config


class BatteryModuleTestCase(unittest.TestCase):
    def setUp(self):
        c = Config()
        c.over_voltage_hysteresis_time = 0.01
        self.module = BatteryModule(c)
        for i in range(4):
            cell = BatteryCell(c)
            cell.voltage = 3.8
            self.module.cells.append(cell)
        self.module.voltage = 24.0
        self.module.temperatures.append(20.0)
        self.module.temperatures.append(22.0)
        self.module.update()

    def test_average_cell_voltage(self):
        self.assertEqual(self.module.average_cell_voltage, 3.8)
        self.module.cells[0].voltage = 3.4
        self.assertEqual(self.module.average_cell_voltage, 3.7)

    def test_low_cell_voltage(self):
        self.module.cells[0].voltage = 3.5
        self.assertEqual(self.module.low_cell_voltage, 3.5)

    def test_high_cell_voltage(self):
        self.module.cells[0].voltage = 4.0
        self.assertEqual(self.module.high_cell_voltage, 4.0)

    def test_lowest_cell_voltage(self):
        self.assertEqual(self.module.lowest_cell_voltage, 3.8)
        self.module.cells[0].voltage = 3.6
        self.module.update()
        self.assertEqual(self.module.lowest_cell_voltage, 3.6)

    def test_highest_cell_voltage(self):
        self.assertEqual(self.module.highest_cell_voltage, 3.8)
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

    def test_over_temperature_alert(self):
        self.module.temperatures = [61, 61]
        self.assertTrue(self.module.over_temperature_alert)

    def test_under_temperature_alert(self):
        self.module.temperatures = [14, 14]
        self.assertTrue(self.module.under_temperature_alert)

    def test_over_temperature_alerts(self):
        self.module.temperatures = [61, 61]
        self.assertEqual(self.module.alerts, [OVER_TEMPERATURE])
        self.assertTrue(self.module.alert)

    def test_under_temperature_alerts(self):
        self.module.temperatures = [12, 12]
        self.assertEqual(self.module.alerts, [UNDER_TEMPERATURE])
        self.assertTrue(self.module.alert)

    def test_over_voltage_alerts(self):
        self.module.cells[3].voltage = 4.125
        self.assertEqual(self.module.alerts, [OVER_VOLTAGE])
        self.assertTrue(self.module.alert)

    def test_under_voltage_alerts(self):
        self.module.cells[3].voltage = 3.575
        self.assertEqual(self.module.alerts, [UNDER_VOLTAGE])
        self.assertTrue(self.module.alert)

    def test_over_temperature_fault(self):
        self.module.temperatures = [70, 70]
        self.assertTrue(self.module.over_temperature_fault)

    def test_under_temperature_fault(self):
        self.module.temperatures = [9, 9]
        self.assertTrue(self.module.under_temperature_fault)

    def test_comms_fault(self):
        self.module.comms_fault = True
        self.assertTrue(self.module.comms_fault)

    def test_over_temperature_faults(self):
        self.module.temperatures = [66, 66]
        self.assertEqual(self.module.faults, [OVER_TEMPERATURE])
        self.assertTrue(self.module.fault)

    def test_under_temperature_faults(self):
        self.module.temperatures = [9, 9]
        self.assertEqual(self.module.faults, [UNDER_TEMPERATURE])
        self.assertTrue(self.module.fault)

    def test_over_voltage_faults(self):
        self.module.cells[1].voltage = 4.2
        self.module.cells[2].voltage = 4.2
        self.module.cells[3].voltage = 4.2
        self.assertEqual(self.module.faults, [])
        sleep(0.01)
        self.assertEqual(self.module.faults, [OVER_VOLTAGE])
        self.assertTrue(self.module.fault)

    def test_under_voltage_faults(self):
        self.module.cells[1].voltage = 3.35
        self.module.cells[2].voltage = 3.35
        self.module.cells[3].voltage = 3.35
        self.assertEqual(self.module.faults, [UNDER_VOLTAGE])
        self.assertTrue(self.module.fault)

    def test_comms_faults(self):
        self.module.comms_fault = True
        self.assertEqual(self.module.faults, [COMMS])
        self.assertTrue(self.module.fault)
