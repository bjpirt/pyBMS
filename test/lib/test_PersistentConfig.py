import os
import json
import unittest
from os import path  # type: ignore
from lib import PersistentConfig

TEST_CONFIG = "/tmp/config.json"


def remove_json():
    try:
        os.remove(TEST_CONFIG)
    except Exception:
        pass


def remove_py():
    try:
        os.remove("config_json.py")
    except Exception:
        pass


class TestConfig(PersistentConfig):
    def __init__(self, defaults={}, config_file=TEST_CONFIG):
        self.test_value = 1

        super().__init__(defaults, config_file)


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        remove_json()
        remove_py()
        return super().setUp()

    def test_load_builtins(self):
        c = TestConfig()
        self.assertEqual(c.test_value, 1)

    def test_load_default(self):
        conf = {"test_value": 4}
        c = TestConfig(conf)
        self.assertEqual(c.test_value, 4)

    def test_load_config_json(self):
        conf = {"test_value": 3}
        with open(TEST_CONFIG, "w") as fp:
            json.dump(conf, fp)
        c = TestConfig({}, TEST_CONFIG)
        self.assertEqual(c.test_value, 3)

    def test_save(self):
        self.assertFalse(path.exists(TEST_CONFIG))
        c = TestConfig({}, TEST_CONFIG)
        c.test_value = 12
        c.save()
        self.assertTrue(path.exists(TEST_CONFIG))
        with open(TEST_CONFIG, "r") as fp:
            savedConfig = json.load(fp)
        self.assertEqual(savedConfig["test_value"], 12)
