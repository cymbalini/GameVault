import json

def getInventory() -> list:
    with open('data/inventory.json', 'r') as file:
        data = json.load(file)
        return data


def addToInventoryToJSON(entry:list):

    currentInventory = getInventory()
    currentInventory.append(entry)

    with open('data/inventory.json', 'w') as file:
        json.dump(currentInventory, file, indent=4)

