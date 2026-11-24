import hashlib
import json
import shutil
import sqlite3
from pathlib import Path


class SQLiteStorage:

    SECRET_SALT = "GameVault_RPG_Salt_123!"

    def __init__(self, file_path="data/gamevault.db",
                 backup_path="data/backup/gamevault.db.bak",
                 legacy_json_path="data/inventory.json"):
        source_folder = Path(__file__).resolve().parent
        self.file_path = self._absolute_path(file_path, source_folder)
        self.backup_path = self._absolute_path(backup_path, source_folder)
        self.legacy_json_path = self._absolute_path(legacy_json_path, source_folder)

    def _absolute_path(self, path, source_folder):
        path = Path(path)
        return path if path.is_absolute() else source_folder / path

    def _gold_hash(self, gold):
        try:
            number = float(gold)
            if number.is_integer():
                gold = int(number)
        except (TypeError, ValueError):
            pass
        value = f"{gold}{self.SECRET_SALT}"
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _connect(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.file_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _create_tables(self, connection):
        connection.execute("""
            CREATE TABLE IF NOT EXISTS inventories (
                inventory_id INTEGER PRIMARY KEY,
                character_name TEXT NOT NULL,
                max_weight_kg REAL NOT NULL CHECK (max_weight_kg > 0),
                gold REAL NOT NULL DEFAULT 0,
                gold_hash TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS inventory_items (
                item_id INTEGER PRIMARY KEY,
                inventory_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                name TEXT NOT NULL,
                weight_kg REAL NOT NULL CHECK (weight_kg >= 0),
                gold_value REAL NOT NULL CHECK (gold_value >= 0),
                rarity TEXT NOT NULL CHECK (rarity IN ('Common', 'Rare', 'Epic', 'Legendary')),
                quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
                base_damage REAL,
                hit_multiplier REAL,
                durability_percent REAL,
                defense_class INTEGER,
                equipment_slot TEXT,
                magic_resistance REAL,
                healing_power INTEGER,
                FOREIGN KEY (inventory_id) REFERENCES inventories(inventory_id) ON DELETE CASCADE
            )
        """)

    def load(self):
        connection = self._connect()
        try:
            self._create_tables(connection)
            row = connection.execute(
                "SELECT COUNT(*) AS amount FROM inventories"
            ).fetchone()
            if row["amount"] == 0:
                self._migrate_into_database(connection)
            self._remove_old_tables(connection)

            state_row = connection.execute(
                "SELECT * FROM inventories WHERE inventory_id = ?", (1,)
            ).fetchone()
            if state_row is None:
                state = {"gold": 0, "inventory": [], "max_weight_kg": 200,
                         "character_name": "Bohater"}
                with connection:
                    self._write_state(connection, state)
                state_row = connection.execute(
                    "SELECT * FROM inventories WHERE inventory_id = ?", (1,)
                ).fetchone()

            state = {
                "gold": state_row["gold"], "gold_hash": state_row["gold_hash"],
                "max_weight_kg": state_row["max_weight_kg"],
                "character_name": state_row["character_name"], "inventory": [],
            }
            rows = connection.execute(
                "SELECT * FROM inventory_items WHERE inventory_id = ? ORDER BY item_id",
                (state_row["inventory_id"],)
            ).fetchall()
            for row in rows:
                item = {"item_id": row["item_id"], "type": row["item_type"],
                        "name": row["name"], "weight_kg": row["weight_kg"],
                        "gold_value": row["gold_value"], "rarity": row["rarity"]}
                if row["quantity"] != 1:
                    item["count"] = row["quantity"]
                for field in ("base_damage", "hit_multiplier", "durability_percent",
                              "defense_class", "equipment_slot", "magic_resistance",
                              "healing_power"):
                    if row[field] is not None:
                        item[field] = row[field]
                state["inventory"].append(item)
        finally:
            connection.close()

        if state["gold_hash"] != self._gold_hash(state["gold"]):
            print("UWAGA: Wykryto zmianę złota. Złoto zostaje wyzerowane.")
            state["gold"] = 0
            self.save(state, make_backup=False)
        return state

    def _migrate_into_database(self, connection):
        old_state = None
        old_tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = ?", ("table",)
        ).fetchall()}
        if "game_state" in old_tables:
            row = connection.execute("SELECT gold FROM game_state WHERE id = ?", (1,)).fetchone()
            if row is not None:
                items = []
                if "items" in old_tables:
                    for old_item in connection.execute("SELECT * FROM items").fetchall():
                        item = dict(old_item)
                        item["type"] = item.get("item_type", "other")
                        items.append(item)
                old_state = {"gold": row["gold"], "inventory": items}
        if old_state is None:
            old_state = self._read_legacy_json()
        if old_state is None:
            return

        try:
            with connection:
                self._write_state(connection, old_state)
                if "items" in old_tables:
                    connection.execute("DROP TABLE items")
                if "game_state" in old_tables:
                    connection.execute("DROP TABLE game_state")
            if self.legacy_json_path.exists():
                archive = self.legacy_json_path.with_suffix(self.legacy_json_path.suffix + ".bak")
                if not archive.exists():
                    shutil.copy2(self.legacy_json_path, archive)
        except (sqlite3.Error, OSError, KeyError, TypeError, ValueError) as error:
            print(f"Nie udało się przenieść starego zapisu: {error}")

    def _remove_old_tables(self, connection):
        """Czyści stary schemat po przeniesieniu danych do nowych tabel."""
        inventory_exists = connection.execute(
            "SELECT 1 FROM inventories WHERE inventory_id = ?", (1,)
        ).fetchone()
        if inventory_exists is None:
            return
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = ?", ("table",)
        ).fetchall()}
        with connection:
            if "items" in tables:
                connection.execute("DROP TABLE items")
            if "game_state" in tables:
                connection.execute("DROP TABLE game_state")

    def _write_state(self, connection, state):
        gold = state.get("gold", 0)
        connection.execute(
            """INSERT INTO inventories
               (inventory_id, character_name, max_weight_kg, gold, gold_hash)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(inventory_id) DO UPDATE SET
               character_name=excluded.character_name,
               max_weight_kg=excluded.max_weight_kg,
               gold=excluded.gold, gold_hash=excluded.gold_hash""",
            (1, state.get("character_name", "Bohater"),
             float(state.get("max_weight_kg", 200)), gold, self._gold_hash(gold))
        )
        connection.execute("DELETE FROM inventory_items WHERE inventory_id = ?", (1,))
        for item in state.get("inventory", []):
            self._insert_item(connection, item)

    def save(self, state, make_backup=True):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if make_backup and self.file_path.exists():
            self.backup_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(self.file_path, self.backup_path)
            except OSError:
                print("Nie udało się utworzyć kopii bazy SQLite.")
        connection = self._connect()
        try:
            self._create_tables(connection)
            with connection:
                self._write_state(connection, state)
        finally:
            connection.close()

    def get_inventory_statistics(self):
        """Zwraca proste podsumowanie przedmiotów pogrupowane według rzadkości."""
        connection = self._connect()
        try:
            rows = connection.execute(
                """SELECT inventory_items.rarity,
                          COUNT(inventory_items.item_id) AS item_count,
                          SUM(inventory_items.weight_kg) AS total_weight_kg,
                          SUM(inventory_items.gold_value) AS total_gold_value,
                          AVG(inventory_items.gold_value) AS average_gold_value
                   FROM inventories
                   LEFT JOIN inventory_items
                     ON inventory_items.inventory_id = inventories.inventory_id
                   WHERE inventories.inventory_id = ?
                   GROUP BY inventory_items.rarity
                   HAVING COUNT(inventory_items.item_id) > 0
                   ORDER BY inventory_items.rarity""",
                (1,)
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()

    def _insert_item(self, connection, item):
        item_type = str(item.get("type", item.get("item_type", "other"))).lower()
        if item_type in {"item", "miscitem"}:
            item_type = "other"
        values = (item.get("item_id", item.get("id")), 1, item_type, item["name"],
                  item.get("weight_kg", item.get("weight")),
                  item.get("gold_value", item.get("value")), item["rarity"],
                  int(item.get("quantity", item.get("count", 1))),
                  item.get("base_damage", item.get("damage")), item.get("hit_multiplier", 1.0),
                  item.get("durability_percent", 100),
                  item.get("defense_class", item.get("defense")), item.get("equipment_slot"),
                  item.get("magic_resistance"), item.get("healing_power"))
        connection.execute(
            """INSERT INTO inventory_items
               (item_id, inventory_id, item_type, name, weight_kg, gold_value,
                rarity, quantity, base_damage, hit_multiplier, durability_percent,
                defense_class, equipment_slot, magic_resistance, healing_power)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            values
        )

    def _read_legacy_json(self):
        if not self.legacy_json_path.exists():
            return None
        try:
            with open(self.legacy_json_path, "r", encoding="utf-8") as file:
                state = json.load(file)
            return state if type(state) is dict else None
        except (json.JSONDecodeError, OSError):
            print("Nie udało się odczytać starego zapisu JSON.")
            return None

    def recover(self):
        if self.backup_path.exists():
            try:
                shutil.copy2(self.backup_path, self.file_path)
                print("Przywrócono bazę z kopii zapasowej.")
                return self.load()
            except OSError:
                print("Nie udało się przywrócić kopii bazy SQLite.")
        return self.load()
