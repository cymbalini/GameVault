from abc import ABC, abstractmethod
import math


class Item(ABC):

    RARITIES = {"Common", "Rare", "Epic", "Legendary"}
    TYPE_NAME = "item"

    def __init__(self, item_id, name, weight_kg, gold_value, rarity):
        weight_kg = float(weight_kg)
        gold_value = float(gold_value)
        if rarity not in self.RARITIES:
            raise ValueError("Rzadkość musi być Common, Rare, Epic lub Legendary.")
        if not math.isfinite(weight_kg) or weight_kg <= 0:
            raise ValueError("Waga przedmiotu musi być większa od zera.")
        if not math.isfinite(gold_value) or gold_value < 0:
            raise ValueError("Wartość przedmiotu nie może być ujemna.")

        self._item_id = int(item_id)
        self._name = str(name)
        self._weight_kg = weight_kg
        self._gold_value = gold_value
        self._rarity = rarity

    @property
    def item_id(self):
        return self._item_id

    @property
    def name(self):
        return self._name

    @property
    def weight_kg(self):
        return self._weight_kg

    @property
    def gold_value(self):
        return self._gold_value

    @property
    def rarity(self):
        return self._rarity

    @property
    def item_type(self):
        return self.__class__.__name__

    @property
    def estimated_value(self):
        return self.calculate_gold_value()

    @abstractmethod
    def calculate_effective_power(self) -> float:
        pass

    def calculate_gold_value(self):
        return self._gold_value

    def to_dict(self):
        return {
            "type": self.TYPE_NAME,
            "item_id": self._item_id,
            "name": self._name,
            "weight_kg": self._weight_kg,
            "gold_value": self._gold_value,
            "rarity": self._rarity,
        }

    @classmethod
    def from_dict(cls, data):
        from . import ITEM_REGISTRY

        item_type = str(data.get("type", data.get("item_type", "other"))).lower()
        if item_type in {"item", "miscitem"}:
            item_type = "other"
        item_class = ITEM_REGISTRY.get(item_type)
        if item_class is None:
            raise ValueError(f"Nieznany typ przedmiotu: {item_type!r}.")
        return item_class.from_dict(data)

    @classmethod
    def _base_values(cls, data):
        return (
            data["item_id"], data["name"], data["weight_kg"],
            data["gold_value"], data["rarity"]
        )

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __lt__(self, other):
        if not hasattr(other, "calculate_gold_value"):
            return NotImplemented
        return (self.calculate_gold_value(), self.item_id) < (
            other.calculate_gold_value(), other.item_id
        )

    def __str__(self):
        return f"{self._name} ({self._rarity})"
