import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.models import Item, Inventory, Weapon, Armor, Potion


def test_valid_objects():
    item = Item(1, "miecz", 2.5, 30, "Rare")
    inventory = Inventory(10)
    inventory.add_item(item)

    assert item.item_id == 1
    assert inventory.total_weight_kg == 2.5


def test_invalid_rarity_is_rejected():
    try:
        Item(2, "potka", 0.2, 5, "Uncommon")
    except ValueError:
        return
    assert False, "przedmiot powinien odrzucać rzadkość spoza danego zestawu"


def test_items_can_be_sorted():
    items = [
        Item(1, "c", 0.1, 100, "Epic"),
        Item(2, "a", 0.2, 2, "Common"),
        Item(3, "b", 4, 25, "Rare"),
    ]

    items.sort()
    assert [item.name for item in items] == ["a","b","c"]


def test_inventory_round_trip():
    original = Inventory(12)
    original.add_item(Item(1, "luk", 1.5, 20, "Rare"))
    original.add_item(Weapon(2, "miecz", 2, 40, "Epic", 15))

    saved_data = original.to_dict()
    restored = Inventory.from_dict(saved_data)

    assert original == restored
    assert isinstance(restored.items[1], Weapon)


def test_subclasses_use_their_own_value_calculation():
    weapon = Weapon(1, "miecz", 2, 10, "Rare", 20)
    armor = Armor(2, "zbroja", 5, 10, "Epic", 10)
    potion = Potion(3, "mikstura", 0.2, 5, "Common", 40)

    assert weapon.calculate_gold_value() == 50
    assert armor.calculate_gold_value() == 25
    assert potion.calculate_gold_value() == 45

    items = [weapon, armor, potion]
    items.sort()
    assert items == [armor, potion, weapon]

    restored = Item.from_dict(weapon.to_dict())
    assert restored == weapon


if __name__ == "__main__":
    test_valid_objects()
    test_invalid_rarity_is_rejected()
    test_items_can_be_sorted()
    test_inventory_round_trip()
    test_subclasses_use_their_own_value_calculation()
    print("Test Przeszedl pomyslnie")
