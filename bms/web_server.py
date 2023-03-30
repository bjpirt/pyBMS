from microdot import Microdot  # type: ignore
from hal.wifi import connect
from .bms import Bms
from .config import Config
from .pages.bms_ui import bmsUi
from .pages.bms_config import bmsConfig


class WebServer:
    def __init__(self, bms: Bms, config: Config) -> None:
        self.__bms = bms
        self.__config = config
        self.__app = app = Microdot()

        @app.get("/")
        def get_bms_ui():
            return bmsUi, 200, {'Content-Type': 'text/html'}

        @app.get("/config")
        def get_config_ui():
            return bmsConfig, 200, {'Content-Type': 'text/html'}

        @app.get("/config.json")
        def get_config():
            return self.__config.get_dict()

        @app.put("/config.json")
        def set_config(req):
            self.__config.apply_config(req.json)
            self.__config.save_config()
            return self.__config.get_dict()

        @app.get("/status.json")
        def get_status():
            return self.__bms.battery_pack.get_dict()

        try:
            import _thread
            _thread.start_new_thread(self.__run, ())
        except:
            import threading
            thread = threading.Thread(target=self.__run, args=())
            thread.daemon = True
            thread.start()

    def __run(self):
        connect(self.__config.wifi_network, self.__config.wifi_password)
        self.__app.run(port=6001)
