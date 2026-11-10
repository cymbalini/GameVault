from .Item import Item
from .Weapon import Weapon
from .Armor import Armor
from .Potion import Potion
from .MiscItem import MiscItem
from .Inventory import HeroInventoryManager, Inventory

ITEM_REGISTRY = {
    "weapon": Weapon,
    "armor": Armor,
    "potion": Potion,
    "other": MiscItem,
}

__all__ = [
    "Item", "Inventory", "HeroInventoryManager", "Weapon", "Armor",
    "Potion", "MiscItem", "ITEM_REGISTRY"
]

