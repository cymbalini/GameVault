from data import *
from validators import *

MAXWEIGHT = 200


def showInventory(inventory=None):
    if inventory is None:
        inventory = getInventory()
    print("\n" + "=" * 40)
    print("INVENTORY")
    print("=" * 40)
    print("-" * 105)
    print(
        f"|name" + " " * 16 + "|" + "count" + " " * 15 + "|" + "weight" + " " * 14 + "|" + "rarity" + " " * 14 + "|" + "value" + " " * 15 + "|")
    print("-" * 105)
    for i in inventory:
        print(f"|{i['name']:<20}|{i['count']:<20}|{i['weight']:<20}|{i['rarity']:<20}|{i['value']:<20}|")
    print("-" * 105)
    print(f"total {getWeightOfInventory()} of weight points in inventory.")
    print(f"Masz przy sobie {getGold()}szt. zlota")


def showFilteredInventoryBy():
    validcategory = getValidCategory("podaj kategorie: ")
    showInventory(sorted(getInventory(), key=lambda x: x[validcategory], reverse=False))


def addInventory() -> None:
    name = getNonEmptyString("podaj nazwe:\n")
    count = getIntInput("podaj ilosc:\n", min_val=1)

    current_weight = getWeightOfInventory()
    if current_weight >= MAXWEIGHT:
        print(f"Ekwipunek jest pełny! ({current_weight}/{MAXWEIGHT})")
        return

    max_weight_per_item = (MAXWEIGHT - current_weight) / count
    weight = getFloat(f"podaj wage max({max_weight_per_item:.2f}): \n", 0.1, max_weight_per_item)
    rarity = getValidRarity("podaj rarity:\n")
    value = getFloat("podaj wartosc:\n")

    addToInventoryToJSON(
        {"id": len(getInventory()), "name": name, "count": count, "weight": weight, "rarity": rarity, "value": value})
    print("Przedmiot został pomyślnie dodany do ekwipunku!")


def getWeightOfInventory() -> float:
    out = 0.0
    for i in getInventory():
        out += i["weight"] * i["count"]
    return out


def showSortedInventoryByRarity():
    rarity = getValidRarity("Podaj rarity:\n")
    showInventory([x for x in getInventory() if x['rarity'] == rarity])


def handleAddGold() -> None:
    amount = getIntInput("Podaj ilość złota do dodania: ", min_val=1)
    modifyGold(amount)
    print(f"Pomyślnie dodano {amount} szt. złota. Aktualny stan: {getGold()}")


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
            if getWeightOfInventory() > MAXWEIGHT:
                print(f"Błąd eksportu: Przekroczono maksymalny udźwig ({getWeightOfInventory()}/{MAXWEIGHT}).")
            else:
                exportToCSV()
            return True
        case "7":
            handleAddGold()
            return True
        case "8" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            return False
        case "9":
            recover_game_state()
            return True
        case _:
            print("Błąd: Nieznana opcja. Wybierz wartość od 1 do 8.")
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
    print("6. Eksport danych do csv")
    print("7. Dodaj złoto")
    print("8. Wyjście z programu")
    print("-" * 40)