from .Item import Item


class Armor(Item):

    TYPE_NAME = "armor"

    def __init__(self, item_id, name, weight_kg, gold_value, rarity,
                 defense_class, equipment_slot="body", magic_resistance=0):
        super().__init__(item_id, name, weight_kg, gold_value, rarity)
        self._defense_class = int(defense_class)
        self._equipment_slot = str(equipment_slot).strip()
        self._magic_resistance = float(magic_resistance)
        if self._defense_class < 0:
            raise ValueError("Klasa obrony nie może być ujemna.")
        if not self._equipment_slot:
            raise ValueError("Slot wyposażenia nie może być pusty.")
        if not 0 <= self._magic_resistance <= 100:
            raise ValueError("Odporność na magię musi mieścić się w zakresie 0-100%.")

    @property
    def defense_class(self):
        return self._defense_class

    @property
    def defense(self):
        return self._defense_class

    @property
    def equipment_slot(self):
        return self._equipment_slot

    @property
    def magic_resistance(self):
        return self._magic_resistance

    def calculate_effective_power(self) -> float:
        return self.defense_class + self.magic_resistance / 10

    def calculate_gold_value(self):
        return self.gold_value + self.defense_class * 1.5

    def to_dict(self):
        data = super().to_dict()
        data["defense_class"] = self.defense_class
        data["equipment_slot"] = self.equipment_slot
        data["magic_resistance"] = self.magic_resistance
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            *cls._base_values(data),
            data.get("defense_class", data.get("defense", 0)),
            data.get("equipment_slot", "body"),
            data.get("magic_resistance", 0)
        )
