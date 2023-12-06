import paho.mqtt.client as mqtt


class PahoMqttClient:
    def __init__(self, client_id, host, keepalive=100) -> None:
        self._host = host
        self._keepalive = keepalive
        self._client = mqtt.Client(client_id=client_id)
        self._client.on_message = self._on_message
        self._callback = None

    def connect(self):
        self._client.connect(self._host, keepalive=self._keepalive)

    def set_callback(self, callback):
        self._callback = callback

    def subscribe(self, topic):
        self._client.subscribe(topic)

    def publish(self, topic, payload):
        self._client.publish(topic, payload)

    def check_msg(self):
        self._client.loop(timeout=0.01)

    def _on_message(self, client, userdata, msg):
        if self._callback:
            self._callback(msg.topic, msg.payload.decode("utf-8"))
