# ruff: noqa: E722
from hal.network import NetworkConnectionInterface
from .bms_interface import BmsInterface
from hal import get_interval, Memory
from config import Config
from mqtt import MQTTClient  # type: ignore
import json
from typing import Dict, Union
try:
    import uasyncio as asyncio  # type: ignore
except ImportError:
    import asyncio


class MqttOutput:
    def __init__(self, config: Config, bms: BmsInterface, network: NetworkConnectionInterface) -> None:
        self._config = config
        self.enabled = self._config.mqtt_enabled is True
        self.connected = False
        self._memory = Memory()
        self._last_values: Dict[str, Union[str, int, float, None]] = {}
        self._full_publish_interval = get_interval()
        self._full_publish_interval.set(self._config.mqtt_full_output_interval)
        if self.enabled:
            self._bms = bms
            self._network = network
            self._client = MQTTClient("pyBms", self._config.mqtt_host)
            self._client.set_callback(self._sub_cb)
            self._publish_interval = get_interval()
            self._publish_interval.set(self._config.mqtt_output_interval)

    def _connect(self) -> None:
        if not self.connected and self._network.connected:
            try:
                print(f"Connecting to MQTT server: {self._config.mqtt_host}")
                self._client.connect()
                self._client.subscribe(f"{self._config.mqtt_topic_prefix}/set-config/#")
                print("Connected to MQTT")
                self.connected = True
            except OSError:
                self.connected = False
                print("Failed to connect to MQTT")

    def _publish(self):
        if self._publish_interval.ready and self._network.connected:
            self._publish_bms_data()
            self._publish_config()
            self._publish_stats()

    def _publish_bms_data(self):
        self._connect()
        self._publish_interval.reset()
        if self.connected:
            self._publish_topic("/voltage", self._bms.battery_pack.voltage)
            self._publish_topic("/soc", self._bms.state_of_charge)
            for module_index, module in enumerate(self._bms.battery_pack.modules):
                self._publish_topic(
                    f"/modules/{module_index}/voltage", module.voltage)
                self._publish_topic(f"/modules/{module_index}/fault", int(module.fault))
                self._publish_topic(f"/modules/{module_index}/alert", int(module.alert))
                for temp_index, temp in enumerate(module.temperatures):
                    self._publish_topic(
                        f"/modules/{module_index}/temperature/{temp_index}", temp)
                for cell_index, cell in enumerate(module.cells):
                    self._publish_topic(
                        f"/modules/{module_index}/cells/{cell_index}/voltage", cell.voltage)
                    self._publish_topic(
                        f"/modules/{module_index}/cells/{cell_index}/fault", int(cell.fault))
                    self._publish_topic(
                        f"/modules/{module_index}/cells/{cell_index}/alert", int(cell.alert))
                    self._publish_topic(
                        f"/modules/{module_index}/cells/{cell_index}/balancing", int(cell.balancing))

    def _publish_config(self):
        for (key, value) in self._config.get_dict().items():
            self._publish_topic(f"/config/{key}", value)

    def _publish_stats(self):
        self._publish_topic("/memory/free", self._memory.free)
        self._publish_topic("/memory/alloc", self._memory.alloc)

    def _should_publish(self, topic: str, value: Union[int, bool, float]) -> bool:
        if topic not in self._last_values or value != self._last_values[topic]:
            self._last_values[topic] = value
            return True
        return False

    def _publish_topic(self, topic: str, value: Union[int, bool, float]) -> None:
        if self._should_publish(topic, value):
            to_send = json.dumps({"value": value})
            self._client.publish(f"{self._config.mqtt_topic_prefix}{topic}", to_send)

    def _sub_cb(self, topic: str, msg) -> None:
        try:
            setting = topic.replace(f"{self._config.mqtt_topic_prefix}/set-config/", "")
            data = json.loads(msg)
            print(f"Setting '{setting}' to '{data['value']}'")
            self._config.set_value(setting, data["value"])
            self._config.save()
        except:  # pylint: disable=bare-except
            print("Error decoding json from MQTT")

    async def main(self):
        while True:
            if self.enabled and self._network.connected:
                self._publish()
                try:
                    await asyncio.sleep_ms(1)
                except:  # pylint: disable=bare-except
                    await asyncio.sleep(0.001)
                if self.connected:
                    self._client.check_msg()
                if self._full_publish_interval.ready:
                    self._full_publish_interval.reset()
                    self._last_values = {}
