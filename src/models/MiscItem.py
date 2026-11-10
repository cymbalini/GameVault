from .Item import Item


class MiscItem(Item):

    TYPE_NAME = "other"

    def calculate_effective_power(self) -> float:
        return 0.0

    @classmethod
    def from_dict(cls, data):
        return cls(*cls._base_values(data))
