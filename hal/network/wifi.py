from typing import Union

from config import Config

from .network_connection_interface import NetworkConnectionInterface

MPY = True
try:
    from network import WLAN, STA_IF  # type: ignore
    import uasyncio as asyncio  # type: ignore
except ModuleNotFoundError:
    MPY = False


class WiFi(NetworkConnectionInterface):
    def __init__(self, config: Config) -> None:
        self.ssid = config.wifi_network
        self.password = config.wifi_password
        if MPY:
            self.wlan: Union[WLAN, None] = None

    async def connect(self):
        if MPY:
            while True:
                self.wlan = WLAN(STA_IF)
                if not self.wlan.isconnected():
                    print(f"Connecting to WiFi [{self.ssid}]")
                    self.wlan.active(True)
                    self.wlan.connect(self.ssid, self.password)
                    while not self.connected:
                        await asyncio.sleep(1)
                        print("Connecting to WiFi")
                    print(f"Connected to network. IP Address: {self.wlan.ifconfig()[0]}")
                else:
                    await asyncio.sleep(1)

    @property
    def connected(self):
        return self.wlan.isconnected() if MPY and self.wlan else False
