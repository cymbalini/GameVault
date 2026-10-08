from data import *
from validators import *

def displayInventory():
    print("\n" + "=" * 40)
    print("INVENTORY")
    print("=" * 40)
    for i in INVENTORY:
        print(f"name: {i['name']}, count: {i['count']}")
    print("-" * 40)

def showFilteredInventoryBy(category: str):
    validCategory = validateCategory(category)
    print("\n" + "=" * 40)
    print(f"INVENTORY SORTED BY {category}")
    print("=" * 40)
    for i in sorted(INVENTORY, key=lambda x: x[validCategory], reverse=False):
        print(f"name: {i['name']}, count: {i['count']}")
    print("-" * 40)

def addInventory()-> None:
    name = getNonEmptyString("podaj nazwe")
    count = getIntInput("podaj ilosc")
    weight = getIntFloat("podaj wage: ", 0.1, 99)
    INVENTORY.append({"id": len(INVENTORY),"name": name, "count": count, "weight": weight})


def handleMenuChoice(prompt: str) -> bool:
    match getNonEmptyString(prompt):
        case "1":
            printMenu()
            return True
        case "2":
            displayInventory()
            return True
        # case "3": #TODO
        #     showCraftableItems()
        #     showCrafting()
        case "4":
            showFilteredInventoryBy(getNonEmptyString("podaj kategorie"))
            return True
        case "5" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            # Zakończenie pętli głównej
            return False
        case "6":
            #test
            addInventory()
            return True
        case _:
            print("Błąd: Nieznana opcja. Wybierz wartość od 1 do 5.")
            return True

def printMenu():
    print("\n" + "=" * 40)
    print(" SYSTEM ZARZĄDZANIA KAWIARNIĄ GameVault")
    print("=" * 40)
    print("1. Wyświetl aktualne menu")
    print("2. Wyswietl aktualny ekwipunek")
    print("3. Wyswietl craftingi")
    print("4. Wyswietl aktualny ekwipunek filtrowany")
    print("5. Wyjście z programu")
    print("-" * 40)