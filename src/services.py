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
            choice = self.validator.getNonEmptyString("Wybierz opcję [1-16]: ")
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
            case "11":
                self.show_inventory_statistics()
            case "12":
                self.select_hero()
            case "13":
                self.add_hero()
            case "14":
                self.search_inventory()
            case "15":
                self.show_hero_summaries()
            case "16":
                self.transfer_item()
            case _:
                print("Błąd: nieznana opcja. Wybierz wartość od 1 do 16.")
        return True
    def show_inventory(self, items=None):
        if items is None:
            items = self.repository.getItems()

        print("\n" + "=" * 40)
        print("EKWIPUNEK BOHATERA")
        print("=" * 40)
        print(f"{'ID':<6}{'Typ':<10}{'Przedmiot':<30}{'Waga kg':<12}{'Rzadkość':<14}{'Wycena':<12}")
        print("-" * 84)
        for item in items:
            print(f"{item.item_id:<6}{item.item_type:<10}{item.get_display_name():<30}{item.weight_kg:<12.2f}"
                  f"{item.rarity:<14}{item.estimated_value:<12.2f}")

        weight = sum(item.weight_kg for item in items)
        print("-" * 84)
        print(f"Łączna waga pokazanych przedmiotów: {weight:.2f} kg")
        max_weight = self.repository.getInventory().max_weight_kg
        print(f"Waga całego plecaka: {self.repository.getWeight():.2f} / {max_weight:g} kg")
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

        item_id = self.repository.getNextItemId()
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
        max_weight = self.repository.getInventory().max_weight_kg
        if self.repository.getWeight() > max_weight:
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
        if item_count == 0:
            print("Ekwipunek jest pusty. Nie ma czego sprzedać.")
            return
        print(f"Sprzedano {item_count} przedmiotów za {total_value:.2f} złota.")
        print(f"Nowy stan złota: {gold_total:.2f}.")

    def show_inventory_statistics(self):
        minimum = self.validator.getFloat(
            "Minimalna łączna wartość rzadkości (0 = wszystkie): ", min_value=0
        )
        statistics = self.repository.getInventoryStatistics(minimum)
        if not statistics:
            print("Brak grup spełniających podany próg wartości.")
            return

        print("\nPODSUMOWANIE WEDŁUG RZADKOŚCI")
        print(f"{'Rzadkość':<14}{'Sztuki':<10}{'Waga kg':<12}{'Suma złota':<14}{'Średnia wartość':<16}")
        for row in statistics:
            rarity = row["rarity"] or "Brak przedmiotów"
            print(f"{rarity:<14}{row['item_count']:<10}"
                  f"{row['total_weight_kg']:<12.2f}{row['total_gold_value']:<14.2f}"
                  f"{row['average_gold_value']:<16.2f}")

    def search_inventory(self):
        phrase = self.validator.getNonEmptyString("Fragment nazwy: ")
        rarity = self.validator.getRarityOrAll("Rzadkość (albo all): ")
        minimum = self.validator.getFloat("Minimalna wartość przedmiotu: ", min_value=0)
        sort_by = self.validator.getSearchSort("Sortuj według (name/weight_kg/gold_value/rarity/item_type): ")
        items = self.repository.searchItems(phrase, rarity, minimum, sort_by)
        if not items:
            print("Nie znaleziono pasujących przedmiotów.")
            return
        self.show_inventory(items)

    def show_hero_summaries(self):
        minimum = self.validator.getFloat(
            "Minimalna wartość plecaka (0 = pokaż wszystkie): ", min_value=0
        )
        rows = self.repository.getHeroSummaries(minimum)
        if not rows:
            print("Brak bohaterów spełniających podany próg.")
            return

        print("\nRAPORT PLECAKÓW")
        print(f"{'ID':<6}{'Bohater':<20}{'Waga':<12}{'Wolne miejsce':<16}{'Wartość':<12}{'Status'}")
        for row in rows:
            status = "PRZECIĄŻONY" if row["free_weight_kg"] < 0 else "OK"
            print(f"{row['inventory_id']:<6}{row['character_name']:<20}"
                  f"{row['total_weight_kg']:.2f}/{row['max_weight_kg']:.2f} kg  "
                  f"{row['free_weight_kg']:<16.2f}{row['total_gold_value']:<12.2f}{status}")

    def transfer_item(self):
        items = self.repository.getItems()
        if not items:
            print("Aktywny bohater nie ma przedmiotów do przeniesienia.")
            return
        heroes = [hero for hero in self.repository.getHeroes()
                  if hero["inventory_id"] != self.repository.active_inventory_id]
        if not heroes:
            print("Dodaj drugiego bohatera, aby przenieść przedmiot.")
            return

        print("\nPRZEDMIOTY AKTYWNEGO BOHATERA")
        for item in items:
            print(f"{item.item_id}. {item.name} ({item.weight_kg:.2f} kg)")
        item_id = self.validator.getInt("ID przedmiotu: ", min_value=0)
        print("\nBOHATEROWIE DOCELOWI")
        for hero in heroes:
            print(f"{hero['inventory_id']}. {hero['character_name']}")
        target_id = self.validator.getInt("ID bohatera docelowego: ", min_value=1)
        try:
            self.repository.transferItem(item_id, target_id)
            print("Przedmiot przeniesiono.")
        except ValueError as error:
            print(f"Transfer anulowany: {error}")

    def select_hero(self):
        heroes = self.repository.getHeroes()
        print("\nDOSTĘPNI BOHATEROWIE")
        for hero in heroes:
            marker = " (aktywny)" if hero["inventory_id"] == self.repository.active_inventory_id else ""
            print(f"{hero['inventory_id']}. {hero['character_name']}{marker}")
        hero_id = self.validator.getInt("Podaj ID bohatera: ", min_value=1)
        try:
            hero = self.repository.selectHero(hero_id)
            print(f"Aktywny bohater: {hero['character_name']} (ID {hero_id}).")
        except ValueError as error:
            print(error)

    def add_hero(self):
        name = self.validator.getNonEmptyString("Podaj imię bohatera: ")
        max_weight = self.validator.getFloat(
            "Podaj maksymalny udźwig plecaka w kg: ", min_value=0.01
        )
        try:
            hero_id = self.repository.createHero(name, max_weight)
            self.repository.selectHero(hero_id)
            print(f"Dodano bohatera {name} (ID {hero_id}) i ustawiono go jako aktywnego.")
        except ValueError as error:
            print(f"Nie udało się dodać bohatera: {error}")

    def print_menu(self):
        heroes = self.repository.getHeroes()
        active_hero = next(
            hero for hero in heroes
            if hero["inventory_id"] == self.repository.active_inventory_id
        )
        print("\n" + "=" * 40)
        print(" GAMEVAULT - EKWIPUNEK BOHATERA")
        print(f"Aktywny bohater: {active_hero['character_name']} (ID {active_hero['inventory_id']})")
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
        print("10. Sprzedaj cały ekwipunek")
        print("11. Statystyki według rzadkości")
        print("12. Zmień aktywnego bohatera")
        print("13. Dodaj bohatera")
        print("14. Szukaj przedmiotów")
        print("15. Raport plecaków bohaterów")
        print("16. Przenieś przedmiot do innego bohatera")
        print("=" * 40)
