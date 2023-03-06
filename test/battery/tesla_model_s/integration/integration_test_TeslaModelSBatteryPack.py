from typing import List, Union
import threading
import unittest
from unittest.mock import MagicMock

from battery.tesla_model_s.TeslaModelSBatteryPack import TeslaModelSBatteryPack
from battery.tesla_model_s.TeslaModelSNetworkGateway import TeslaModelSNetworkGateway

import time
from test.tesla_bms_emulator.CompoundSerial import CompoundSerial
from test.tesla_bms_emulator import TeslaBmsEmulator
import serial

bmsSerialPort1a = serial.Serial('port1-end-a', 230400, timeout=0.01)
bmsSerialPort1b = serial.Serial('port1-end-b', 230400, timeout=0.01)
bmsSerialPort2a = serial.Serial('port2-end-a', 230400, timeout=0.01)
bmsSerialPort2b = serial.Serial('port2-end-b', 230400, timeout=0.01)
bmsSerialPort3a = serial.Serial('port3-end-a', 230400, timeout=0.01)
bmsSerialPort3b = serial.Serial('port3-end-b', 230400, timeout=0.01)

compoundPort1 = CompoundSerial(bmsSerialPort1a, bmsSerialPort3b)
compoundPort2 = CompoundSerial(bmsSerialPort2a, bmsSerialPort1b)
compoundPort3 = CompoundSerial(bmsSerialPort3a, bmsSerialPort2b)

# Compound serial
#  Server
# Tx = port1-end-a send
# Rx = port3-end-b
#
# BMS1
# Tx = port2-end-a
# Rx = port1-end-b
#
# BMS2
# Tx = port3-end-a
# Rx = port2-end-b

bms1 = TeslaBmsEmulator(compoundPort2, "bms1")
bms1.address = 9
bms2 = TeslaBmsEmulator(compoundPort3, "bms2")
bms2.address = 10
done = threading.Event()


def run_bms(name):
    while not done.is_set():
        bms1.process()
        bms2.process()


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
        gateway = TeslaModelSNetworkGateway(compoundPort1)
        pack = TeslaModelSBatteryPack(2, gateway)

        timeoutTime = time.time() + 5
        while not pack.ready and time.time() < timeoutTime:
            pass
        self.assertEqual(len(pack.modules), 2)
        pack.update()
        self.assertEqual(pack.modules[0].voltage, 20.295)
        self.assertEqual(pack.modules[1].voltage, 20.295)
