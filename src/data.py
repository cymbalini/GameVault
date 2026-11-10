import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


class JsonStorage:

    SECRET_SALT = "GameVault_RPG_Salt_123!"

    def __init__(self, file_path="data/inventory.json",
                 backup_path="data/backup/inventory.json.bak",
                 old_file_path="data/json/savegame.json"):
        source_folder = Path(__file__).resolve().parent
        self.file_path = self._make_absolute(file_path, source_folder)
        self.backup_path = self._make_absolute(backup_path, source_folder)
        self.old_file_path = self._make_absolute(old_file_path, source_folder)

    def _make_absolute(self, path, source_folder):
        path = Path(path)
        if not path.is_absolute():
            path = source_folder / path
        return path

    def _gold_hash(self, gold):
        text = f"{gold}{self.SECRET_SALT}"
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def load(self):
        if not self.file_path.exists():
            if self.old_file_path.exists():
                try:
                    with open(self.old_file_path, "r", encoding="utf-8") as file:
                        old_state = json.load(file)
                    print("Przenoszenie starego zapisu do data/inventory.json.")
                    self.save(old_state, make_backup=False)
                    return old_state
                except (json.JSONDecodeError, OSError):
                    print("Nie udało się odczytać starego zapisu.")
            return self.recover()

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                state = json.load(file)
            if type(state) is not dict:
                raise ValueError("Niepoprawny format zapisu.")

            gold = state.get("gold", 0)
            if state.get("gold_hash") != self._gold_hash(gold):
                print("UWAGA: Wykryto zmianę złota. Złoto zostaje wyzerowane.")
                state["gold"] = 0
                state["gold_hash"] = self._gold_hash(0)
                self.save(state)

            if type(state.get("inventory")) is not list:
                state["inventory"] = []
            return state
        except (json.JSONDecodeError, OSError, ValueError, AttributeError):
            print("Błąd odczytu zapisu. Przywracanie kopii...")
            return self.recover()

    def save(self, state, make_backup=True):
        state["gold_hash"] = self._gold_hash(state.get("gold", 0))
        self._atomic_write(
            self.file_path,
            lambda file: json.dump(state, file, indent=4),
            make_backup,
            self.backup_path
        )

    def recover(self):
        if self.backup_path.exists():
            try:
                with open(self.backup_path, "r", encoding="utf-8") as file:
                    state = json.load(file)
                if type(state) is dict:
                    print("Pomyślnie przywrócono dane z kopii zapasowej.")
                    self.save(state, make_backup=False)
                    return state
            except (json.JSONDecodeError, OSError):
                print("Nie udało się odczytać kopii zapasowej.")

        print("Tworzenie pustego zapisu gry.")
        state = {"gold": 0, "gold_hash": self._gold_hash(0), "inventory": []}
        self.save(state, make_backup=False)
        return state

    def _atomic_write(self, path, write_function, make_backup=True, backup_path=None):
        path = Path(path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        if make_backup and path.exists():
            backup = Path(backup_path).resolve() if backup_path else path.with_suffix(path.suffix + ".bak")
            backup.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(path, backup)
            except OSError:
                print("Nie udało się utworzyć kopii zapasowej.")

        temporary = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        )
        temporary_path = Path(temporary.name)
        try:
            write_function(temporary)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary.close()
            os.replace(temporary_path, path)
        except Exception:
            temporary.close()
            if temporary_path.exists():
                temporary_path.unlink()
            raise


