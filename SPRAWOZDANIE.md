# Sprawozdanie z Zadania 3 – GameVault

**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Temat:** Dziedziczenie, polimorfizm i zarządzanie ekwipunkiem RPG  
**Autor:** Krzysztof Nowak  
**Data:** 10.11.2026

---

## 1. Cel zadania

Celem było rozbudowanie GameVault o hierarchię klas przedmiotów i zastosowanie polimorfizmu. Program pozwala dodawać przedmioty do plecaka z kontrolą limitu wagi, zapisywać stan gry, eksportować ekwipunek do CSV oraz sprzedawać cały ekwipunek za złoto.

## 2. Struktura programu

* `src/models/Item.py` – klasa bazowa `Item`, walidacja danych i wspólna metoda wyceny.
* `src/models/Weapon.py` – broń z obrażeniami.
* `src/models/Armor.py` – pancerz z poziomem ochrony.
* `src/models/Potion.py` – mikstura z siłą leczenia.
* `src/models/Inventory.py` – agregat przechowujący przedmioty i pilnujący maksymalnej wagi.
* `src/repository.py` – `GameRepository`, który zarządza kolekcją przedmiotów i stanem złota.
* `src/data.py` – `JsonStorage`, zapis atomowy, kopia zapasowa i kontrola sumy złota.
* `src/CsvExporter.py` – eksport przedmiotów do CSV, także gdy mają różne pola.
* `src/validators.py` – pobieranie i sprawdzanie danych wpisywanych w konsoli.
* `src/services.py` – `GameVaultApp`, menu i obsługa działań użytkownika.
* `src/tests/test_models.py` – testy encji, agregatu, sortowania i serializacji.

Dane gry są zapisywane w `src/data/inventory.json`, kopia zapasowa w `src/data/backup/inventory.json.bak`, a eksport w `src/exports/loot_table.csv`.

## 3. Dziedziczenie i polimorfizm

`Weapon`, `Armor` i `Potion` dziedziczą po `Item`. Każda podklasa nadpisuje `calculate_gold_value()`: broń uwzględnia obrażenia, pancerz poziom ochrony, a mikstura siłę leczenia. Ekwipunek, sortowanie, sprzedaż i eksport korzystają ze wspólnego interfejsu przedmiotów.

Przykład nadpisania metody:

```python
class Weapon(Item):
    def calculate_gold_value(self):
        return self.gold_value + self.damage * 2
```

`Inventory.add_item()` sprawdza wagę przed dodaniem. Jeśli przedmiot przekroczyłby `max_weight_kg`, metoda zgłasza `ValueError`. `GameRepository` zapisuje zmiany i nie umieszcza tej logiki w obsłudze menu.

## 4. Funkcje programu

Menu pozwala wyświetlić, filtrować i sortować ekwipunek, dodawać przedmioty oraz złoto, eksportować CSV, przywrócić zapis z kopii i sprzedać cały ekwipunek. Opcja 10 sprzedaje wszystkie przedmioty według ich wyceny, dodaje uzyskaną kwotę do złota i zapisuje pusty ekwipunek. Każda modyfikacja stanu tworzy kopię poprzedniego zapisu.

Eksport CSV zbiera kolumny ze wszystkich typów przedmiotów, dlatego wiersze broni, pancerza i mikstury mogą zawierać różne dodatkowe pola.

## 5. Weryfikacja

Testy modeli uruchamia się poleceniem:

```text
python src/tests/test_models.py
```

Testy sprawdzają poprawne tworzenie obiektów, odrzucenie niedozwolonej rzadkości, sortowanie przedmiotów, serializację i odtworzenie ekwipunku zawierającego podklasę `Weapon` oraz wyceny polimorficzne.

Sprawdzono także eksport mieszanej listy `Item`, `Weapon`, `Armor` i `Potion` oraz sprzedaż przedmiotów z naliczeniem złota. Testy modeli i te sprawdzenia zakończyły się powodzeniem.
