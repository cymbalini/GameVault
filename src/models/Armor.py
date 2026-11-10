from .Item import Item


class Armor(Item):

    def __init__(self, item_id, name, weight_kg, gold_value, rarity, defense):
        super().__init__(item_id, name, weight_kg, gold_value, rarity)
        self._defense = int(defense)
        if self._defense < 0:
            raise ValueError("Ochrona pancerza nie może być ujemna.")

    @property
    def defense(self):
        return self._defense

    def calculate_gold_value(self):
        return self.gold_value + self.defense * 1.5

    def to_dict(self):
        data = super().to_dict()
        data["defense"] = self.defense
        return data
