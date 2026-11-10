from .Item import Item


class Potion(Item):

    TYPE_NAME = "potion"

    def __init__(self, item_id, name, weight_kg, gold_value, rarity, healing_power):
        super().__init__(item_id, name, weight_kg, gold_value, rarity)
        self._healing_power = int(healing_power)
        if self._healing_power < 0:
            raise ValueError("Siła leczenia nie może być ujemna.")

    @property
    def healing_power(self):
        return self._healing_power

    def calculate_effective_power(self) -> float:
        return float(self.healing_power)

    def calculate_gold_value(self):
        return self.gold_value + self.healing_power

    def to_dict(self):
        data = super().to_dict()
        data["healing_power"] = self.healing_power
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(*cls._base_values(data), data["healing_power"])
