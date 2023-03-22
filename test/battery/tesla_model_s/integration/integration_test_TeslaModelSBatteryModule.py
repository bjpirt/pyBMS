import threading
import unittest
from unittest.mock import MagicMock
from battery.tesla_model_s.TeslaModelSBatteryModule import TeslaModelSBatteryModule
from battery.tesla_model_s.TeslaModelSNetworkGateway import TeslaModelSNetworkGateway
import serial
from bms import Config
from emulator.tesla_bms import TeslaBmsEmulator

bmsSerialPort = serial.Serial('port1-end-a', 115200, timeout=0.01)
bms = TeslaBmsEmulator(bmsSerialPort)
bms.address = 1
done = threading.Event()


def run_bms(name):
    while not done.is_set():
        bms.process()


class TeslaModelSBatteryModuleTestCase(unittest.TestCase):

    def setUp(self):
        self.bmsThread = threading.Thread(target=run_bms, args=(1,))
        self.bmsThread.start()
        return super().tearDown()

    def tearDown(self):
        done.set()
        self.bmsThread.join()

        return super().tearDown()

    def test_update(self):
        moduleSerialPort = serial.Serial('port1-end-b', 115200, timeout=0.01)
        gateway = TeslaModelSNetworkGateway(moduleSerialPort)
        module = TeslaModelSBatteryModule(1, gateway, Config())

        module.update()

        self.assertEqual(module.voltage, 20.295)
        self.assertEqual(module.cells[0].voltage, 3.8)
        self.assertEqual(module.cells[1].voltage, 3.9)
        self.assertEqual(module.cells[2].voltage, 4.0)
        self.assertEqual(module.cells[3].voltage, 4.1)
        self.assertEqual(module.cells[4].voltage, 4.2)
        self.assertEqual(module.cells[5].voltage, 4.3)
        self.assertEqual(module.temperatures[0], 25.343)
        self.assertEqual(module.temperatures[1], 25.343)
