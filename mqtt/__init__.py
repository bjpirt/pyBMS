# ruff: noqa: F401
try:
    from umqtt.robust import MQTTClient as MQTTClient  # type: ignore
except ModuleNotFoundError:
    from .paho_mqtt_client import PahoMqttClient as MQTTClient
