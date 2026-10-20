import json
from typing import Any


def getInventory() -> list:
    try:
        with open('data/inventory.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print('Inventory file not found, creating new one')
        open('data/inventory.json', 'w')
        return []
    except PermissionError:
        print('Missing permissions')
        return []
    except json.decoder.JSONDecodeError:
        print('JSON decode error')
        return []


def addToInventoryToJSON(entry:dict[str,Any]) -> None:

    currentInventory = getInventory()
    currentInventory.append(entry)

    try:
        with open('data/inventory.json', 'w') as file:
            json.dump(currentInventory, file, indent=4)
    except:
        print('something went wrong while adding to inventory')

