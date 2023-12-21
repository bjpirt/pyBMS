import os
import json


def exists(filename: str) -> bool:
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


class PersistentConfig:
    def __init__(self, initial_config={}, file="config.json"):
        self.__file = file

        self.update(initial_config)
        self.read()

    def get_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def read(self):
        data = None
        if exists(self.__file):
            with open(self.__file, 'r', encoding="UTF-8") as file:
                data = file.read()
                if data:
                    new_config = json.loads(data)
                    self.update(new_config)

    def set_value(self, key: str, value):
        if hasattr(self, key):
            if type(getattr(self, key)) == type(value) or type(value) == type(None):
                setattr(self, key, value)
            else:
                print(
                    f"Config types did not match: {key} ({type(getattr(self, key))}) ({type(value)})")
        else:
            print("Attribute does not exist")

    def update(self, new_config: dict) -> None:
        for (key, value) in new_config.items():
            self.set_value(key, value)

    def save(self):
        with open(self.__file, 'w', encoding="utf-8") as file:
            json.dump(self.get_dict(), file)
