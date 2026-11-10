from CsvExporter import CsvExporter
from src.models import Weapon, Armor, Potion, MiscItem
from repository import GameRepository
from validators import InputValidator


class GameVaultApp:

    MAX_WEIGHT_KG = 200

    def __init__(self, repository=None, validator=None, exporter=None):
        self.repository = repository or GameRepository()
        self.validator = validator or InputValidator()
        self.exporter = exporter or CsvExporter()

    def run(self):
        self.print_menu()
        running = True
        while running:
            choice = self.validator.getNonEmptyString("Wybierz opcję [1-10]: ")
            running = self.handle_choice(choice)

    def handle_choice(self, choice):

        match choice.lower():
            case "1":
                self.print_menu()
            case "2":
                self.show_inventory()
            case "3":
                self.show_by_rarity()
            case "4":
                self.show_sorted_inventory()
            case "5":
                self.add_item()
            case "6":
                self.export_inventory()
            case "7":
                self.add_gold()
            case "8" | "q" | "exit":
                print("Zamykanie programu. Do widzenia!")
                return False
            case "9":
                self.repository.recover()
            case "10":
                self.sell_all_items()
            case _:
                print("Błąd: nieznana opcja. Wybierz wartość od 1 do 10.")
        return True
    def show_inventory(self, items=None):
        if items is None:
            items = self.repository.getItems()

        print("\n" + "=" * 40)
        print("EKWIPUNEK BOHATERA")
        print("=" * 40)
        print(f"{'ID':<6}{'Typ':<10}{'Nazwa':<20}{'Waga kg':<12}{'Rzadkość':<14}{'Wycena':<12}")
        print("-" * 74)
        for item in items:
            print(f"{item.item_id:<6}{item.item_type:<10}{item.name:<20}{item.weight_kg:<12.2f}"
                  f"{item.rarity:<14}{item.estimated_value:<12.2f}")

        weight = sum(item.weight_kg for item in items)
        print("-" * 74)
        print(f"Łączna waga pokazanych przedmiotów: {weight:.2f} kg")
        print(f"Waga całego plecaka: {self.repository.getWeight():.2f} / {self.MAX_WEIGHT_KG} kg")
        print(f"Potencjał bojowy: {self.repository.getInventory().calculate_total_combat_power():.2f}")
        print(f"Złoto: {self.repository.getGold()}")

    def show_by_rarity(self):
        rarity = self.validator.getRarity("Podaj rzadkość: ")
        items = [item for item in self.repository.getItems()
                    if item.rarity == rarity]
        self.show_inventory(items)

    def show_sorted_inventory(self):
        category = self.validator.getCategory(
            "Sortuj (item_id/name/weight_kg/estimated_value/rarity/item_type): "
        )
        items = sorted(self.repository.getItems(), key=lambda item: getattr(item, category))
        self.show_inventory(items)

    def add_item(self):
        item_type = self.validator.getItemType("Typ (Weapon/Armor/Potion/Other): ")
        name = self.validator.getNonEmptyString("Podaj nazwę przedmiotu: ")
        weight = self.validator.getFloat("Podaj wagę w kg: ", min_value=0.01)
        rarity = self.validator.getRarity("Podaj rzadkość: ")
        value = self.validator.getFloat("Podaj wartość w złocie: ", min_value=0)

        items = self.repository.getItems()
        item_id = max((item.item_id for item in items), default=-1) + 1
        try:
            creators = {
                "Weapon": self._create_weapon,
                "Armor": self._create_armor,
                "Potion": self._create_potion,
                "Other": self._create_misc_item,
            }
            item = creators[item_type](item_id, name, weight, value, rarity)
            self.repository.addItem(item)
            print("Przedmiot dodany do ekwipunku.")
        except ValueError as error:
            print(f"Nie dodano przedmiotu: {error}")

    def _create_weapon(self, item_id, name, weight, value, rarity):
        damage = self.validator.getFloat("Podaj obrażenia bazowe: ", min_value=0)
        multiplier = self.validator.getFloat("Podaj mnożnik trafienia: ", min_value=0)
        durability = self.validator.getFloat("Podaj trwałość (0-100%): ", 0, 100)
        return Weapon(item_id, name, weight, value, rarity, damage, multiplier, durability)

    def _create_armor(self, item_id, name, weight, value, rarity):
        defense = self.validator.getInt("Podaj poziom ochrony: ", min_value=0)
        slot = self.validator.getNonEmptyString("Podaj slot wyposażenia: ")
        resistance = self.validator.getFloat("Podaj odporność na magię (0-100%): ", 0, 100)
        return Armor(item_id, name, weight, value, rarity, defense, slot, resistance)

    def _create_potion(self, item_id, name, weight, value, rarity):
        healing = self.validator.getInt("Podaj siłę leczenia: ", min_value=0)
        return Potion(item_id, name, weight, value, rarity, healing)

    def _create_misc_item(self, item_id, name, weight, value, rarity):
        return MiscItem(item_id, name, weight, value, rarity)

    def export_inventory(self):
        if self.repository.getWeight() > self.MAX_WEIGHT_KG:
            print("Eksport przerwany: przekroczono maksymalny udźwig plecaka.")
            return
        try:
            self.exporter.export(self.repository.getItems())
        except OSError as error:
            print(f"Nie udało się zapisać CSV: {error}")

    def add_gold(self):
        amount = self.validator.getInt("Ile złota dodać? ", min_value=1)
        total = self.repository.addGold(amount)
        print(f"Dodano {amount} szt. złota. Aktualny stan: {total}.")

    def sell_all_items(self):
        item_count, total_value, gold_total = self.repository.sellAllItems()
        if item_count != 0:
            print("Ekwipunek jest pusty. Nie ma czego sprzedać.")
            return
        print(f"Sprzedano {item_count} przedmiotów za {total_value:.2f} złota.")
        print(f"Nowy stan złota: {gold_total:.2f}.")

    def print_menu(self):
        print("\n" + "=" * 40)
        print(" GAMEVAULT - EKWIPUNEK BOHATERA")
        print("=" * 40)
        print("1. Wyświetl menu")
        print("2. Wyświetl ekwipunek")
        print("3. Filtruj według rzadkości")
        print("4. Sortuj ekwipunek")
        print("5. Dodaj przedmiot")
        print("6. Eksportuj do CSV")
        print("7. Dodaj złoto")
        print("8. Wyjście")
        print("9. Przywróć zapis z kopii")
        # print("10. Sprzedaj cały ekwipunek")
        print("=" * 40)
