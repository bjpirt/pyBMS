from .mqtt_output import MqttOutput
from .web_server import WebServer  # type: ignore
from hal.network import WiFi
from .bms import Bms
from config import Config
try:
    import uasyncio as asyncio  # type: ignore
except ImportError:
    import asyncio


class Network:
    def __init__(self, bms: Bms, config: Config) -> None:
        self.__webserver = WebServer(bms, config)
        self.__wifi = WiFi(config)
        self.__mqtt = MqttOutput(config, bms, self.__wifi)

        try:
            import _thread
            try:
                _thread.stack_size(16*1024)
            except ValueError:
                pass
            _thread.start_new_thread(self.__thread, ())
        except ModuleNotFoundError:
            import threading
            thread = threading.Thread(target=self.__thread, args=())
            thread.daemon = True
            thread.start()

    def __thread(self):
        try:
            asyncio.run(self.__main())
        except OSError:
            print("Error connecting to WiFi")

    async def __main(self):
        print("Starting asyncio thread")
        asyncio.create_task(self.__wifi.connect())
        asyncio.create_task(self.__webserver.start())
        asyncio.create_task(self.__mqtt.main())
        while True:
            await asyncio.sleep(10)
