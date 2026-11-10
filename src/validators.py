class InputValidator:

    RARITIES = ["Common", "Rare", "Epic", "Legendary"]
    CATEGORIES = [
        "item_id", "name", "weight_kg", "gold_value", "estimated_value",
        "rarity", "item_type"
    ]
    ITEM_TYPES = ["Weapon", "Armor", "Potion", "Other"]

    def getInt(self, prompt, min_value=None, max_value=None):
        while True:
            raw = input(prompt).strip()
            try:
                value = int(raw)
                if min_value is not None and value < min_value:
                    print(f"Błąd: wartość musi wynosić co najmniej {min_value}.")
                    continue
                if max_value is not None and value > max_value:
                    print(f"Błąd: wartość nie może być większa niż {max_value}.")
                    continue
                return value
            except ValueError:
                print("Błąd: wpisz liczbę całkowitą.")

    def getFloat(self, prompt, min_value=None, max_value=None):
        while True:
            raw = input(prompt).strip().replace(",", ".")
            try:
                value = float(raw)
                if min_value is not None and value < min_value:
                    print(f"Błąd: wartość musi wynosić co najmniej {min_value}.")
                    continue
                if max_value is not None and value > max_value:
                    print(f"Błąd: wartość nie może być większa niż {max_value:.2f}.")
                    continue
                return value
            except ValueError:
                print("Błąd: wpisz liczbę.")

    def getNonEmptyString(self, prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("Błąd: pole nie może być puste.")

    def getCategory(self, prompt):
        while True:
            value = input(prompt).strip().lower()
            if value in self.CATEGORIES:
                return value
            print("Podaj jedną z dostępnych właściwości przedmiotu.")

    def getRarity(self, prompt):
        while True:
            value = input(prompt).strip().title()
            if value in self.RARITIES:
                return value
            print("Podaj rzadkość: Common, Rare, Epic lub Legendary.")

    def getItemType(self, prompt):
        while True:
            value = input(prompt).strip().title()
            if value in self.ITEM_TYPES:
                return value
            print("Wybierz typ: Weapon, Armor, Potion lub Other.")
