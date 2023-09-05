from .bms_interface import BmsInterface
from hal import get_interval
from .config import Config
from mqtt import MQTTClient  # type: ignore
import json
from typing import Union


class MqttOutput:
    def __init__(self, config: Config, bms: BmsInterface) -> None:
        self._config = config
        self._bms = bms
        print(self._config.mqtt_host)
        self._client = MQTTClient("pyBms", self._config.mqtt_host)
        self._interval = get_interval()
        self._interval.set(self._config.mqtt_output_interval)
        self.connected = False
        self._connect()

    def _connect(self) -> None:
        if not self.connected:
            try:
                self._client.connect()
            except OSError:
                print("Failed to connect to MQTT")

    def process(self):
        if self._interval.ready:
            self._connect()
            self._interval.reset()
            self._publish("/voltage", self._bms.battery_pack.voltage)
            self._publish("/soc", self._bms.state_of_charge)
            for module_index, module in enumerate(self._bms.battery_pack.modules):
                self._publish(
                    f"/modules/{module_index}/voltage", module.voltage)
                self._publish(f"/modules/{module_index}/fault", int(module.fault))
                self._publish(f"/modules/{module_index}/alert", int(module.alert))
                for temp_index, temp in enumerate(module.temperatures):
                    self._publish(
                        f"/modules/{module_index}/temperature/{temp_index}", temp)
                for cell_index, cell in enumerate(module.cells):
                    self._publish(
                        f"/modules/{module_index}/cells/{cell_index}/voltage", cell.voltage)
                    self._publish(
                        f"/modules/{module_index}/cells/{cell_index}/fault", int(cell.fault))
                    self._publish(
                        f"/modules/{module_index}/cells/{cell_index}/alert", int(cell.alert))

    def _publish(self, topic: str, value: Union[int, bool, float]) -> None:
        self._client.publish(f"{self._config.mqtt_topic_prefix}{topic}", json.dumps(
            {"value": value}))
