from .Bms import Bms
from .Config import Config
from microdot import Microdot
from .pages.bmsUi import bmsUi
from .pages.bmsConfig import bmsConfig
from hal.WiFi import connect

mpy = True
try:
    import _thread
except:
    import threading
    mpy = False


class WebServer:
    def __init__(self, bms: Bms, config: Config) -> None:
        self.__bms = bms
        self.__config = config
        self.__app = app = Microdot()

        @app.get("/")
        def getBmsUi(req):
            return bmsUi, 200, {'Content-Type': 'text/html'}

        @app.get("/config")
        def getConfigUi(req):
            return bmsConfig, 200, {'Content-Type': 'text/html'}

        @app.get("/config.json")
        def getConfig(req):
            return self.__config.getDict()

        @app.put("/config.json")
        def setConfig(req):
            print(req.json)
            self.__config.applyConfig(req.json)
            self.__config.saveConfig()
            return self.__config.getDict()

        @app.get("/status.json")
        def getStatus(req):
            return self.__bms.batteryPack.getDict()

        if mpy:
            thread = _thread.start_new_thread(self.run, ())
        else:
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True
            thread.start()

    def run(self):
        connect(self.__config.wifiNetwork, self.__config.wifiPassword)
        self.__app.run(port=6001)
