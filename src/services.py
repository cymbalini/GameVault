from data import *
from validators import *

MAXWEIGHT = 200

def showInventory(inventory=INVENTORY):
    print("\n" + "=" * 40)
    print("INVENTORY")
    print("=" * 40)
    print("-" * 85)
    print(f"|name" + " " * 16 + "|" + "count" + " " * 15 + "|" + "weight" + " " * 14 + "|" + "rarity" + " "*14 + "|")
    print("-" * 85)
    for i in inventory:
        print(f"|{i['name']:<20}|{i['count']:<20}|{i['weight']:<20}|{i['rarity']:<20}|")
    print("-" * 85)
    print(f"total {getWeightOfInventory()} of weight points in inventory.")

def showFilteredInventoryBy():
    validcategory = getValidCategory("podaj kategorie: ")
    showInventory(sorted(INVENTORY, key=lambda x: x[validcategory], reverse=False))

def addInventory()-> None:
    name = getNonEmptyString("podaj nazwe:\n")
    count = getIntInput("podaj ilosc:\n")
    weight = getFloat(f"podaj wage max({((200-getWeightOfInventory())/count):.2f}): \n", 0.1, 200-getWeightOfInventory())
    rarity = getNonEmptyString("podaj rarity:\n")
    INVENTORY.append({"id": len(INVENTORY),"name": name, "count": count, "weight": weight, "rarity": rarity})

def getWeightOfInventory() -> float:
    out =0.0
    for i in INVENTORY:
        out += i["weight"]*i["count"]
    return out

def showSortedInventoryByRarity():
    rarity = getValidRarity("Podaj rarity:\n")
    showInventory(x for x in INVENTORY if x['rarity'] == rarity)

def handleMenuChoice(prompt: str) -> bool:
    match getNonEmptyString(prompt):
        case "1":
            printMenu()
            return True
        case "2":
            showInventory()
            return True
        case "3":
            showSortedInventoryByRarity()
            return True
        case "4":
            showFilteredInventoryBy()
            return True
        case "5":
            addInventory()
            return True
        case "6":
            #test
            return True
        case "7" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            return False
        case _:
            print("Błąd: Nieznana opcja. Wybierz wartość od 1 do 5.")
            return True

def printMenu():
    print("\n" + "=" * 40)
    print(" SYSTEM ZARZĄDZANIA KAWIARNIĄ GameVault")
    print("=" * 40)
    print("1. Wyświetl aktualne menu")
    print("2. Wyswietl aktualny ekwipunek")
    print("3. Wyswietl filtrowany ekwipunek przez rzadkosc")
    print("4. Wyswietl aktualny ekwipunek filtrowany przez kategorie")
    print("5. Dodaj item")
    print("6. test")
    print("7. Wyjście z programu")
    print("-" * 40)