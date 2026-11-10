import math
from .Item import Item


class Weapon(Item):

    TYPE_NAME = "weapon"

    def __init__(self, item_id, name, weight_kg, gold_value, rarity,
                 base_damage, hit_multiplier=1.0, durability_percent=100):
        super().__init__(item_id, name, weight_kg, gold_value, rarity)
        self._base_damage = float(base_damage)
        self._hit_multiplier = float(hit_multiplier)
        self._durability_percent = float(durability_percent)
        if not math.isfinite(self._base_damage) or self._base_damage < 0:
            raise ValueError("Obrażenia bazowe nie mogą być ujemne.")
        if not math.isfinite(self._hit_multiplier) or self._hit_multiplier < 0:
            raise ValueError("Mnożnik trafienia nie może być ujemny.")
        if not 0 <= self._durability_percent <= 100:
            raise ValueError("Trwałość musi mieścić się w zakresie 0-100%.")

    @property
    def base_damage(self):
        return self._base_damage

    @property
    def damage(self):
        # Zachowanie zgodności ze starszym zapisem i widokiem.
        return self._base_damage

    @property
    def hit_multiplier(self):
        return self._hit_multiplier

    @property
    def durability_percent(self):
        return self._durability_percent

    def calculate_effective_power(self) -> float:
        return self.base_damage * self.hit_multiplier * self.durability_percent / 100

    def calculate_gold_value(self):
        return self.gold_value + self.base_damage * 2

    def to_dict(self):
        data = super().to_dict()
        data["base_damage"] = self.base_damage
        data["hit_multiplier"] = self.hit_multiplier
        data["durability_percent"] = self.durability_percent
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(
            *cls._base_values(data),
            data.get("base_damage", data.get("damage", 0)),
            data.get("hit_multiplier", 1.0),
            data.get("durability_percent", 100)
        )
