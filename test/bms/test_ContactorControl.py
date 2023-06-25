import time
import unittest

from bms import Config, ContactorControl, ContactorState


class ContactorControlTestCase(unittest.TestCase):
    def setUp(self):
        config = Config("config.default.json")
        config.contactor_negative_time = 0.1
        config.contactor_precharge_time = 0.1
        self.control = ContactorControl(config)

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
        self.assertEqual(self.control.state, ContactorState.ALL_ON)
        time.sleep(0.1)
        self.control.process()
        self.assertEqual(self.control.state, ContactorState.ENABLED)
        self.control.disable()
        self.control.process()
        self.assertEqual(self.control.state, ContactorState.DISABLED)
