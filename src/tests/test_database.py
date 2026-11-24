import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

project_folder = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_folder))
sys.path.insert(0, str(project_folder / "src"))

from data import SQLiteStorage
from repository import GameRepository
from src.models import Weapon


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_folder = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_folder.name)
        self.database_path = self.folder / "gamevault.db"
        self.json_path = self.folder / "inventory.json"
        self.storage = SQLiteStorage(
            self.database_path,
            self.folder / "backup.db",
            self.json_path,
        )

    def tearDown(self):
        self.temp_folder.cleanup()

    def test_schema_and_foreign_key_constraints(self):
        self.storage.load()
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = ?", ("table",)
        )}
        self.assertIn("inventories", tables)
        self.assertIn("inventory_items", tables)
        foreign_key = connection.execute(
            "PRAGMA foreign_key_list(inventory_items)"
        ).fetchone()
        self.assertEqual(foreign_key[2], "inventories")
        self.assertEqual(foreign_key[6].upper(), "CASCADE")
        row = connection.execute(
            "SELECT * FROM inventories WHERE inventory_id = ?", (1,)
        ).fetchone()
        self.assertIsInstance(row, sqlite3.Row)
        self.assertIn("character_name", dict(row))

        with self.assertRaises(sqlite3.IntegrityError):
            connection.execute(
                """INSERT INTO inventory_items
                   (item_id, inventory_id, item_type, name, weight_kg,
                    gold_value, rarity) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (1, 999, "weapon", "Miecz", 1, 10, "Rare"),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            connection.execute(
                """INSERT INTO inventory_items
                   (item_id, inventory_id, item_type, name, weight_kg,
                    gold_value, rarity) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (2, 1, "weapon", "Miecz", 1, 10, "Uncommon"),
            )
        connection.close()

    def test_repository_saves_and_reads_inventory(self):
        item = Weapon(3, "Miecz", 2, 25, "Rare", 12)
        self.storage.save({"gold": 15, "max_weight_kg": 40,
                           "inventory": [item.to_dict()]}, make_backup=False)
        repository = GameRepository(self.storage)
        loaded = repository.getInventory()

        self.assertEqual(loaded.max_weight_kg, 40)
        self.assertEqual(loaded.items[0].name, "Miecz")
        self.assertEqual(loaded.items[0].item_type, "Weapon")
        self.assertEqual(repository.getGold(), 15)

    def test_sql_injection_text_is_saved_as_a_name(self):
        strange_name = "Miecz'); DROP TABLE inventory_items;--"
        item = Weapon(4, strange_name, 1, 15, "Common", 4)
        self.storage.save({"gold": 0, "inventory": [item.to_dict()]}, make_backup=False)

        repository = GameRepository(self.storage)
        self.assertEqual(repository.getItems()[0].name, strange_name)
        connection = sqlite3.connect(self.database_path)
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = ?", ("table",)
        )}
        connection.close()
        self.assertIn("inventory_items", tables)

    def test_statistics_join_and_group_items_by_rarity(self):
        items = [
            Weapon(1, "Miecz", 1, 10, "Common", 5).to_dict(),
            Weapon(2, "Topór", 2, 20, "Common", 8).to_dict(),
            Weapon(3, "Łuk", 3, 100, "Epic", 12).to_dict(),
        ]
        self.storage.save({"gold": 0, "inventory": items}, make_backup=False)

        statistics = GameRepository(self.storage).getInventoryStatistics()
        common = next(row for row in statistics if row["rarity"] == "Common")
        self.assertEqual(common["item_count"], 2)
        self.assertEqual(common["total_weight_kg"], 3)
        self.assertEqual(common["total_gold_value"], 30)
        self.assertEqual(common["average_gold_value"], 15)

    def test_deleting_inventory_cascades_to_items(self):
        self.storage.save({"gold": 0, "inventory": [
            Weapon(1, "Topór", 2, 10, "Common", 5).to_dict()
        ]}, make_backup=False)
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("DELETE FROM inventories WHERE inventory_id = ?", (1,))
        remaining = connection.execute(
            "SELECT COUNT(*) FROM inventory_items"
        ).fetchone()[0]
        connection.close()
        self.assertEqual(remaining, 0)

    def test_json_migration_runs_once_and_keeps_backup(self):
        old_data = {"gold": 50, "inventory": [{
            "item_id": 8, "type": "weapon", "name": "Stary miecz",
            "weight_kg": 1, "gold_value": 20, "rarity": "Epic",
            "base_damage": 9,
        }]}
        self.json_path.write_text(json.dumps(old_data), encoding="utf-8")

        migrated = self.storage.load()
        self.assertEqual(migrated["gold"], 50)
        self.assertEqual(migrated["inventory"][0]["name"], "Stary miecz")
        self.assertTrue(self.json_path.with_suffix(".json.bak").exists())

        self.json_path.write_text(json.dumps({"gold": 2, "inventory": []}), encoding="utf-8")
        loaded_again = self.storage.load()
        self.assertEqual(loaded_again["gold"], 50)
        self.assertEqual(len(loaded_again["inventory"]), 1)


if __name__ == "__main__":
    unittest.main()
