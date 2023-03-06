import time
import unittest

from bms import ContactorControl, ContactorState
from hal import DummyContactorGpio


class ContactorControlTestCase(unittest.TestCase):
    def setUp(self):
        self.gpio = DummyContactorGpio()
        self.control = ContactorControl(
            self.gpio, negativeTime=0.1, prechargeTime=0.1)

    def test_switch(self):
        self.assertEqual(self.control.state, ContactorState.DISABLED)
        self.control.enable()
        self.control.process()
        self.assertEqual(self.control.state, ContactorState.NEGATIVE_ON)
        time.sleep(0.1)
        self.control.process()
        self.assertEqual(self.control.state, ContactorState.PRECHARGE_ON)
        time.sleep(0.1)
        self.control.process()
        self.assertEqual(self.control.state, ContactorState.ENABLED)
        self.control.disable()
        self.control.process()
        self.assertEqual(self.control.state, ContactorState.DISABLED)
