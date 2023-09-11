from microdot_asyncio import Microdot  # type: ignore
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
        async def get_bms_ui(_):
            return bms_ui, 200, {'Content-Type': 'text/html'}

        @app.get("/config")
        async def get_config_ui(_):
            return bms_config, 200, {'Content-Type': 'text/html'}

        @app.get("/config.json")
        async def get_config(_):
            return self.__config.get_dict()

        @app.put("/config.json")
        async def set_config(req):
            self.__config.update(req.json)
            self.__config.save()
            return self.__config.get_dict()

        @app.get("/status.json")
        async def get_status(_):
            return self.__bms.get_dict()

    async def start(self):
        await self.__app.start_server(port=self.__config.web_server_port)
