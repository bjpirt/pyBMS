from hal.network import NetworkConnectionInterface
from .bms_interface import BmsInterface
from hal import get_interval
from config import Config
from mqtt import MQTTClient  # type: ignore
import json
from typing import Union
try:
    import uasyncio as asyncio  # type: ignore
except ImportError:
    import asyncio


class MqttOutput:
    def __init__(self, config: Config, bms: BmsInterface, network: NetworkConnectionInterface) -> None:
        self._config = config
        self.enabled = self._config.mqtt_enabled is True
        self.connected = False
        if self.enabled:
            self._bms = bms
            self._network = network
            self._client = MQTTClient("pyBms", self._config.mqtt_host)
            self._interval = get_interval()
            self._interval.set(self._config.mqtt_output_interval)

    def _connect(self) -> None:
        if not self.connected and self._network.connected:
            try:
                print(f"Connecting to MQTT server: {self._config.mqtt_host}")
                self._client.connect()
                print("Connected to MQTT")
                self.connected = True
            except OSError:
                self.connected = False
                print("Failed to connect to MQTT")

    def _publish(self):
        if self._interval.ready and self._network.connected:
            self._connect()
            self._interval.reset()
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

    def _publish_topic(self, topic: str, value: Union[int, bool, float]) -> None:
        self._client.publish(f"{self._config.mqtt_topic_prefix}{topic}", json.dumps(
            {"value": value}))

    async def main(self):
        while True:
            if self.enabled and self._network.connected:
                self._publish()
                await asyncio.sleep_ms(1)
                if self.connected:
                    self._client.check_msg()
