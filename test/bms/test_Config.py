import os
import json
import unittest
from os import path  # type: ignore
from bms import Config
from scripts.data_to_py import write_data


def get_dummy_config():
    with open("config.default.json", "r") as fp:
        return json.load(fp)


def remove_json():
    try:
        os.remove("/tmp/config.json")
    except:
        pass


def remove_py():
    try:
        os.remove("config_json.py")
    except:
        pass


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        remove_json()
        remove_py()
        return super().setUp()

    def test_load_builtins(self):
        c = Config("no-file.json")
        self.assertEqual(c.moduleCount, 2)

    def test_load_default(self):
        c = get_dummy_config()
        c["moduleCount"] = 4
        with open("/tmp/config.json", "w") as fp:
            json.dump(c, fp)
        write_data("config_json.py", "/tmp/config.json")
        c = Config("no-file.json")
        self.assertEqual(c.moduleCount, 4)

    def test_load_config_json(self):
        c = get_dummy_config()
        c["moduleCount"] = 8
        with open("/tmp/config.json", "w") as fp:
            json.dump(c, fp)
        write_data("config_json.py", "/tmp/config.json")
        c = Config("/tmp/config.json")
        self.assertEqual(c.moduleCount, 8)

    def test_save(self):
        self.assertFalse(path.exists("/tmp/config.json"))
        c = Config("/tmp/config.json")
        c.moduleCount = 12
        c.saveConfig()
        self.assertTrue(path.exists("/tmp/config.json"))
        with open("/tmp/config.json", "r") as fp:
            savedConfig = json.load(fp)
        self.assertEqual(savedConfig["moduleCount"], 12)