import csv
import json
import os
import shutil
import tempfile
import hashlib
from pathlib import Path
from typing import Any, Callable
from operator import itemgetter

DB_PATH = Path('data/json/savegame.json')
BACKUP_PATH = Path('data/backup/savegame.json.bak')
CSV_PATH = Path('data/export/lootTable.csv')
SECRET_SALT = "GameVault_RPG_Salt_123!"

def generate_gold_hash(gold_value: int) -> str:
    return hashlib.sha256(f"{gold_value}{SECRET_SALT}".encode('utf-8')).hexdigest()

def getGameState() -> dict:
    if not DB_PATH.exists():
        return recover_game_state()

    try:
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)


        gold = data.get("gold", 0)
        stored_hash = data.get("gold_hash", "")

        if generate_gold_hash(gold) != stored_hash:
            print("UWAGA: Wykryto ręczną modyfikację złota! Złoto zostaje wyzerowane.")
            data["gold"] = 0
            data["gold_hash"] = generate_gold_hash(0)
            saveGameState(data)

        if "inventory" not in data or not isinstance(data["inventory"], list):
            data["inventory"] = []

        return data
    except (json.JSONDecodeError, IOError, AttributeError):
        print("Błąd odczytu pliku zapisu, przywracanie...")
        return recover_game_state()

def saveGameState(state: dict) -> None:
    try:
        atomicWrite(
            DB_PATH,
            lambda file: json.dump(state, file, indent=4),
            makeBackup=True,
            backupPath=BACKUP_PATH
        )
    except Exception:
        print("Błąd przy zapisywaniu stanu gry.")
def getInventory() -> list:
    return getGameState().get("inventory", [])

def addToInventoryToJSON(entry: dict[str, Any]) -> None:
    state = getGameState()
    state["inventory"].append(entry)
    saveGameState(state)

def getGold() -> int:
    return getGameState().get("gold", 0)

def modifyGold(amount: int) -> None:
    state = getGameState()
    current_gold = state.get("gold", 0)
    new_gold = max(0, current_gold + amount)
    state["gold"] = new_gold
    state["gold_hash"] = generate_gold_hash(new_gold)
    saveGameState(state)

def exportToCSV() -> None:
    inventory = getInventory()
    if not inventory:
        print("Ekwipunek jest pusty, nic do wyeksportowania.")
        return

    sortedInventory = sorted(inventory, key=itemgetter('rarity'))
    fieldnames = list(sortedInventory[0].keys())

    def write_csv(file):
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sortedInventory)

    try:
        atomicWrite(CSV_PATH, write_csv, mode='w', encoding='utf-8', makeBackup=False)
        print("Eksport do pliku CSV zakończony pomyślnie.")
    except Exception:
        print("Coś poszło nie tak podczas eksportu CSV.")

def recover_game_state() -> dict:
    if BACKUP_PATH.exists():
        try:
            with open(BACKUP_PATH, 'r', encoding='utf-8') as bak_file:
                recovered_data = json.load(bak_file)
            print("Pomyślnie przywrócono dane.")
            atomicWrite(DB_PATH, lambda f: json.dump(recovered_data, f, indent=4), makeBackup=False)
            return recovered_data
        except (json.JSONDecodeError, IOError):
            print("Błąd pliku kopii zapasowej.")

    print("Tworzenie pustej bazy danych.")
    empty_data = {"gold": 0, "gold_hash": generate_gold_hash(0), "inventory": []}
    atomicWrite(DB_PATH, lambda f: json.dump(empty_data, f, indent=4), makeBackup=False)
    return empty_data


def atomicWrite(filepath: str | Path, writeFunc: Callable[[Any], None], mode: str = 'w', encoding: str = 'utf-8',
                makeBackup: bool = True, backupPath: str | Path = None) -> None:
    path = Path(filepath).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    if makeBackup and path.exists():
        if backupPath:
            backupFile = Path(backupPath).resolve()
            backupFile.parent.mkdir(parents=True, exist_ok=True)
        else:
            backupFile = path.with_suffix(path.suffix + '.bak')

        try:
            shutil.copy2(path, backupFile)
        except Exception:
            print("Nie udało się stworzyć pliku zapasowego")

    kwargs = {'encoding': encoding} if 'b' not in mode else {}
    temp_file = tempfile.NamedTemporaryFile(mode=mode, dir=path.parent, delete=False, **kwargs)
    temp_path = Path(temp_file.name)

    try:
        writeFunc(temp_file)
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_file.close()
        os.replace(temp_path, path)
    except Exception:
        temp_file.close()
        if temp_path.exists():
            temp_path.unlink()
        raise