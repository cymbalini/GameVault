import json
import sqlite3
import sys
from tempfile import TemporaryDirectory
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_folder))
sys.path.insert(0, str(project_folder / "src"))

from data import SQLiteStorage
from repository import GameRepository
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


def test_repository_reads_polymorphic_items_from_sqlite():
    with TemporaryDirectory(dir=project_folder) as folder:
        data_folder = Path(folder)
        storage = SQLiteStorage(
            data_folder / "gamevault.db",
            data_folder / "backup.db",
            data_folder / "legacy.json"
        )
        storage.save({
            "gold": 10,
            "inventory": [
                Weapon(1, "Miecz", 2, 40, "Rare", 20, 1.5, 50).to_dict(),
                Armor(2, "Pancerz", 5, 70, "Epic", 6, "body", 20).to_dict(),
            ],
        }, make_backup=False)

        manager = GameRepository(storage, 10).getInventory()

        assert [item.item_type for item in manager.items] == ["Weapon", "Armor"]
        assert manager.calculate_total_combat_power() == 23


def test_sqlite_migrates_json_and_has_relations():
    with TemporaryDirectory(dir=project_folder) as folder:
        data_folder = Path(folder)
        legacy_path = data_folder / "legacy.json"
        database_path = data_folder / "gamevault.db"
        old_state = {
            "gold": 25,
            "inventory": [
                Weapon(7, "Blade'); DROP TABLE items;--", 1, 30, "Rare", 10).to_dict()
            ],
        }
        with open(legacy_path, "w", encoding="utf-8") as file:
            json.dump(old_state, file)

        storage = SQLiteStorage(
            database_path,
            data_folder / "backup.db",
            legacy_path
        )
        migrated_state = storage.load()
        manager = GameRepository(storage, 10).getInventory()

        assert migrated_state["gold"] == 25
        assert manager.items[0].name == "Blade'); DROP TABLE items;--"
        assert manager.items[0].item_type == "Weapon"

        connection = sqlite3.connect(database_path)
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = ?", ("table",)
        ).fetchall()
        state_columns = connection.execute("PRAGMA table_info(inventories)").fetchall()
        item_columns = connection.execute("PRAGMA table_info(inventory_items)").fetchall()
        foreign_keys = connection.execute("PRAGMA foreign_key_list(inventory_items)").fetchall()
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        connection.close()

        assert ("inventories",) in tables
        assert ("inventory_items",) in tables
        assert next(column for column in state_columns if column[1] == "inventory_id")[5] == 1
        assert next(column for column in item_columns if column[1] == "item_id")[5] == 1
        assert foreign_keys[0][2] == "inventories"
        assert integrity == "ok"


if __name__ == "__main__":
    test_manager_adds_items_and_counts_power()
    test_manager_rejects_overweight_item()
    test_manager_rejects_object_outside_item_contract()
    test_manager_serializes_and_restores_subclasses()
    test_base_item_is_abstract()
    test_repository_reads_polymorphic_items_from_sqlite()
    test_sqlite_migrates_json_and_has_relations()
    print("Manager tests passed.")
