from battery.battery_pack import BatteryPack


class BmsInterface:
    def __init__(self, battery_pack: BatteryPack) -> None:
        self.battery_pack = battery_pack

    def process(self) -> None:
        pass

    def get_dict(self) -> dict:
        return {}

    @property
    def state_of_charge(self) -> float:
        return 0.0

    @property
    def current(self) -> float:
        return 0.0
