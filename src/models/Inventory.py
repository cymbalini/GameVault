from .Item import Item


class Inventory:

    def __init__(self, max_weight_kg):
        if float(max_weight_kg) <= 0:
            raise ValueError("Maksymalna waga musi być większa od zera.")
        self._max_weight_kg = float(max_weight_kg)
        self._items = []

    @property
    def max_weight_kg(self):
        return self._max_weight_kg

    @property
    def items(self):
        return list(self._items)

    @property
    def total_weight_kg(self):
        return sum(item.weight_kg for item in self._items)

    def add_item(self, item):
        if not isinstance(item, Item):
            raise TypeError("Do ekwipunku można dodać tylko obiekt Item.")

        new_weight = self.total_weight_kg + item.weight_kg
        if new_weight > self._max_weight_kg:
            raise ValueError(
                f"Przedmiot przekracza udźwig plecaka: {new_weight:.2f} kg "
                f"/ {self._max_weight_kg:.2f} kg."
            )
        self._items.append(item)

    def find_by_rarity(self, rarity):
        return [item for item in self._items if item.rarity == rarity]

    def sorted_by(self, category):
        return sorted(self._items, key=lambda item: getattr(item, category))

    def to_dict(self):
        return {
            "max_weight_kg": self._max_weight_kg,
            "items": [item.to_dict() for item in self._items],
        }

    @classmethod
    def from_dict(cls, data):
        inventory = cls(data["max_weight_kg"])
        for item_data in data["items"]:
            inventory.add_item(Item.from_dict(item_data))
        return inventory

    def __eq__(self, other):
        if not isinstance(other, Inventory):
            return NotImplemented
        return self.to_dict() == other.to_dict()
