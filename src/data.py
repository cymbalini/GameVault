import csv
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable
from operator import itemgetter

DB_PATH = Path('data/inventory.json')
BACKUP_PATH = Path('data/inventory.json.bak')
CSV_PATH = Path('data/lootTable.csv')

def getInventory() -> list:
    if not DB_PATH.exists():
        print("Brak pliku Json")
        return recover_inventory()

    try:
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print("JSONDecodeError")
        return recover_inventory()


def addToInventoryToJSON(entry: dict[str, Any]) -> None:
    currentInventory = getInventory()
    currentInventory.append(entry)

    try:
        atomicWrite(
            DB_PATH,
            lambda file: json.dump(currentInventory, file, indent=4),
            makeBackup=True
        )
    except Exception:
        print("cos poszlo nie tak przy dodawaniu")


def exportToCSV() -> None:
    inventory = getInventory()
    if not inventory:
        return

    sortedInventory = sorted(inventory, key=itemgetter('rarity'))
    fieldnames = list(sortedInventory[0].keys())

    def write_csv(file):
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sortedInventory)

    try:
        atomicWrite(CSV_PATH, write_csv, mode='w', encoding='utf-8', makeBackup=False)
    except Exception:
        print("cos poszlo nie tak podczas eksportu CSV")


def atomicWrite(filepath: str | Path, writeFunc: Callable[[Any], None], mode: str = 'w', encoding: str = 'utf-8', makeBackup: bool = True) -> None:

    path = Path(filepath).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    if makeBackup and path.exists():
        backupFile = path.with_suffix(path.suffix + '.bak')
        try:
            shutil.copy2(path, backupFile)
        except Exception:
            print("Nieudalo sie stworzyc plkuzapasowego")

    kwargs = {'encoding': encoding} if 'b' not in mode else {}
    temp_file = tempfile.NamedTemporaryFile(
        mode=mode,
        dir=path.parent,
        delete=False,
        **kwargs
    )

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


def recover_inventory() -> list:
    if BACKUP_PATH.exists():
        try:
            with open(BACKUP_PATH, 'r', encoding='utf-8') as bak_file:
                recovered_data = json.load(bak_file)

            print("Pomyślnie przywrócono dane")

            atomicWrite(DB_PATH, lambda f: json.dump(recovered_data, f, indent=4), makeBackup=False)
            return recovered_data
        except (json.JSONDecodeError, IOError) as e:
            print("JSONDecodeError w backupfile")

    print("Tworzenie pusted bazydanych")
    empty_data: list = []
    atomicWrite(DB_PATH, lambda f: json.dump(empty_data, f, indent=4), makeBackup=False)
    return empty_data