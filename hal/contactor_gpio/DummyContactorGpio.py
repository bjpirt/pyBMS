from .ContactorGpio import ContactorGpio


class DummyContactorGpio(ContactorGpio):

    def update(self, negative: bool, precharge: bool, positive: bool):
        print(
            f"Contactor state: negative: {negative} positive: {positive} precharge: {precharge}")
