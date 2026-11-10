from .Item import Item


class Weapon(Item):

    def __init__(self, item_id, name, weight_kg, gold_value, rarity, damage):
        super().__init__(item_id, name, weight_kg, gold_value, rarity)
        self._damage = int(damage)
        if self._damage < 0:
            raise ValueError("Obrażenia nie mogą być ujemne.")

    @property
    def damage(self):
        return self._damage

    def calculate_gold_value(self):
        return self.gold_value + self.damage * 2

    def to_dict(self):
        data = super().to_dict()
        data["damage"] = self.damage
        return data
