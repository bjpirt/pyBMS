from microdot import Microdot  # type: ignore
from hal.wifi import connect
from .bms import Bms
from config import Config
from .pages.bms_ui import bms_ui
from .pages.bms_config import bms_config


class WebServer:
    def __init__(self, bms: Bms, config: Config) -> None:
        self.__bms = bms
        self.__config = config
        self.__app = app = Microdot()

        @app.get("/")
        def get_bms_ui(_):
            return bms_ui, 200, {'Content-Type': 'text/html'}

        @app.get("/config")
        def get_config_ui(_):
            return bms_config, 200, {'Content-Type': 'text/html'}

        @app.get("/config.json")
        def get_config(_):
            return self.__config.get_dict()

        @app.put("/config.json")
        def set_config(req):
            self.__config.update(req.json)
            self.__config.save()
            return self.__config.get_dict()

        @app.get("/status.json")
        def get_status(_):
            return self.__bms.get_dict()

        try:
            import _thread
            try:
                _thread.stack_size(16*1024)
            except ValueError:
                pass
            _thread.start_new_thread(self.__run, ())
        except ModuleNotFoundError:
            import threading
            thread = threading.Thread(target=self.__run, args=())
            thread.daemon = True
            thread.start()

    def __run(self):
        try:
            print(
                f"Connecting to WiFi [{self.__config.wifi_network}] with password [{self.__config.wifi_password}]")
            connect(self.__config.wifi_network, self.__config.wifi_password)
            self.__app.run(port=self.__config.web_server_port)
        except OSError:
            print("Error connecting to WiFi")
