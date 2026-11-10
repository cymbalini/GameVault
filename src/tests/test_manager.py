import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.models import Item, Weapon, Armor, HeroInventoryManager


def test_manager_adds_items_and_counts_power():
    manager = HeroInventoryManager(8)
    manager.add_item(Weapon(1, "Miecz", 2, 40, "Rare", 20, 1.5, 50))
    manager.add_item(Armor(2, "Pancerz", 5, 70, "Epic", 6, "body", 20))

    assert manager.total_weight_kg == 7
    assert manager.calculate_total_combat_power() == 23


def test_manager_rejects_overweight_item():
    manager = HeroInventoryManager(2)
    manager.add_item(Weapon(1, "Sztylet", 1.5, 10, "Common", 5))

    try:
        manager.add_item(Armor(2, "Tarcza", 1, 15, "Common", 2))
    except ValueError:
        pass
    else:
        assert False, "Menedżer powinien odrzucić przedmiot przekraczający udźwig"

    assert len(manager.items) == 1
    assert manager.total_weight_kg == 1.5


def test_manager_rejects_object_outside_item_contract():
    manager = HeroInventoryManager(5)
    try:
        manager.add_item(object())
    except TypeError:
        return
    assert False, "Menedżer powinien wymagać kontraktu Item"


def test_manager_serializes_and_restores_subclasses():
    manager = HeroInventoryManager(10)
    manager.add_item(Weapon(1, "Topór", 3, 50, "Epic", 12, 1.2, 80))
    manager.add_item(Armor(2, "Hełm", 1, 20, "Rare", 4, "head", 10))

    saved = manager.to_dict()
    restored = HeroInventoryManager.from_dict(saved)

    assert manager == restored
    assert [item["type"] for item in saved["items"]] == ["weapon", "armor"]
    assert restored.calculate_total_combat_power() == manager.calculate_total_combat_power()


def test_base_item_is_abstract():
    try:
        Item(1, "Test", 1, 1, "Common")
    except TypeError:
        return
    assert False, "Nie można utworzyć bezpośrednio abstrakcyjnego Item"


if __name__ == "__main__":
    test_manager_adds_items_and_counts_power()
    test_manager_rejects_overweight_item()
    test_manager_rejects_object_outside_item_contract()
    test_manager_serializes_and_restores_subclasses()
    test_base_item_is_abstract()
    print("Manager tests passed.")
