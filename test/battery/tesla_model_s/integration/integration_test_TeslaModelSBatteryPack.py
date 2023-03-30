import threading
import unittest
from battery.tesla_model_s.tesla_model_s_battery_pack import TeslaModelSBatteryPack
from battery.tesla_model_s.tesla_model_s_network_gateway import TeslaModelSNetworkGateway
import time
import serial  # type: ignore
from bms import Config
from emulator.tesla_bms import CompoundSerial, TeslaBmsEmulator

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


def run_bms1(name):
    while not done.is_set():
        bms1.process()


def run_bms2(name):
    while not done.is_set():
        bms2.process()


class TeslaModelSBatteryModuleTestCase(unittest.TestCase):

    def setUp(self):
        self.bmsThread1 = threading.Thread(target=run_bms1, args=(1,))
        self.bmsThread2 = threading.Thread(target=run_bms2, args=(2,))
        self.bmsThread1.start()
        self.bmsThread2.start()
        return super().tearDown()

    def tearDown(self):
        done.set()
        self.bmsThread1.join()
        self.bmsThread2.join()

        return super().tearDown()

    def test_update(self):
        gateway = TeslaModelSNetworkGateway(compoundPort1, Config())
        config = Config()
        config.module_count = 2
        pack = TeslaModelSBatteryPack(gateway, config)

        timeoutTime = time.time() + 5
        while not pack.ready and time.time() < timeoutTime:
            pass
        self.assertEqual(len(pack.modules), 2)
        pack.update()
        self.assertEqual(pack.modules[0].voltage, 20.295)
        self.assertEqual(pack.modules[1].voltage, 20.295)
