# Sprawozdanie z Zadania 4 – GameVault i SQLite

**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Temat:** Relacyjna baza danych SQLite  
**Autor:** Krzysztof Nowak  
**Data:** 24.11.2026

---

## 1. Cel zadania

Celem było zastąpienie plikowego zapisu stanu gry relacyjną bazą SQLite. Ekwipunek nadal korzysta z hierarchii `Item`, `Weapon`, `Armor` i pozostałych podklas, a nowe repozytorium zapisuje przedmioty i złoto w tabelach połączonych relacją klucza obcego.

## 2. Struktura programu

* `src/data.py` – klasa `SQLiteStorage`: tworzenie tabel, odczyt, zapis transakcyjny, kopia bazy oraz jednorazowa migracja starego JSON.
* `src/repository.py` – `GameRepository`, który mapuje rekordy bazy na agregat ekwipunku.
* `src/models/` – klasy domenowe `Item`, `Weapon`, `Armor`, `Potion`, `MiscItem` i `HeroInventoryManager`.
* `src/CsvExporter.py` – eksport ekwipunku do CSV.
* `src/services.py` i `src/validators.py` – menu CLI i walidacja danych.
* `src/tests/test_database.py` – autotesty schematu, relacji, repozytorium i migracji SQLite.
* `src/tests/test_manager.py` – testy menedżera oraz persystencji SQLite.
* `src/tests/test_models.py` – testy modeli i serializacji.

Baza znajduje się w `src/data/gamevault.db`, a kopia zapasowa w `src/data/backup/gamevault.db.bak`. Przy pierwszym uruchomieniu aplikacja przenosi istniejący `src/data/inventory.json` do bazy tylko wtedy, gdy baza nie zawiera jeszcze ekwipunku. JSON jest archiwizowany jako `inventory.json.bak`. Starszy schemat SQLite `game_state`/`items` także jest przenoszony do nowych tabel.

## 3. Schemat relacyjny

```text
INVENTORIES (1) ────────< (wiele) INVENTORY_ITEMS
  inventory_id PK             item_id       PK
  character_name              inventory_id FK -> INVENTORIES.inventory_id
  max_weight_kg               item_type, name, weight_kg, gold_value, rarity
  gold, gold_hash             pola podklas: broń, pancerz, mikstura
```

Tabela `inventories` przechowuje wielu bohaterów, każdy z osobnym limitem udźwigu, stanem złota i jego sumą kontrolną. Tabela `inventory_items` przechowuje przedmioty oraz dyskryminator `item_type`, który pozwala odtworzyć właściwą podklasę. Klucz obcy ma `ON DELETE CASCADE`, więc usunięcie bohatera usuwa jego przedmioty. SQL sprawdza limit większy od zera, nieujemną wagę i wartość, dodatnią ilość oraz rzadkość z dozwolonego zestawu. Menu pozwala dodać bohatera oraz zmienić aktywny ekwipunek.

## 4. Zapis i bezpieczeństwo zapytań

Zmiana stanu odbywa się w transakcji SQLite: aktualizowany jest stan złota, poprzednie rekordy przedmiotów są zastępowane nową listą, a transakcja zatwierdza całość. Przed zapisem istniejąca baza jest kopiowana do pliku backupu.

Wartości użytkownika są przekazywane przez parametry `?`, a nie doklejane do tekstu SQL:

```python
row = connection.execute(
    "SELECT gold, gold_hash FROM inventories WHERE inventory_id = ?",
    (1,)
).fetchone()
```

Podobnie parametryzowane jest dodawanie rekordów. Nazwa przedmiotu zawierająca tekst podobny do SQL jest zapisywana jako zwykła wartość, a tabela pozostaje nienaruszona. Dyskryminator typu jest odczytywany przez rejestr klas, więc baza zachowuje polimorficzne typy przedmiotów.

Wyszukiwanie przedmiotów używa `LIKE`, filtra rzadkości i minimalnej wartości, przekazując dane jako parametry nazwane. Sortowanie wybiera kolumnę z białej listy (`name`, `weight_kg`, `gold_value`, `rarity`, `item_type`); nazwa kolumny nie pochodzi bezpośrednio od użytkownika.

## 5. Analityka SQL

Opcja 11 prezentuje liczbę, łączną wagę i wartość przedmiotów dla każdej rzadkości, a opcja 15 pokazuje sumę wagi, wartość i wolny udźwig wszystkich plecaków. Oba raporty wykonują `LEFT JOIN`, `GROUP BY`, `HAVING` i `COALESCE` po stronie SQLite. Przykład zapytania dla raportu bohaterów:

```sql
SELECT inventories.inventory_id,
       inventories.character_name,
       COALESCE(SUM(inventory_items.weight_kg), 0.0) AS total_weight_kg,
       COALESCE(SUM(inventory_items.gold_value), 0.0) AS total_gold_value,
       inventories.max_weight_kg -
           COALESCE(SUM(inventory_items.weight_kg), 0.0) AS free_weight_kg
FROM inventories
LEFT JOIN inventory_items
  ON inventory_items.inventory_id = inventories.inventory_id
GROUP BY inventories.inventory_id, inventories.character_name,
         inventories.max_weight_kg
HAVING COALESCE(SUM(inventory_items.gold_value), 0.0) >= ?
    OR COALESCE(SUM(inventory_items.weight_kg), 0.0) > inventories.max_weight_kg;
```

Opcja 16 atomowo przenosi przedmiot między bohaterami. Transfer najpierw zmienia przypisanie w otwartej transakcji, a następnie sprawdza limit plecaka. Jeśli limit zostałby przekroczony, metoda zgłasza `ValueError`, a blok `with connection:` wycofuje zmianę.

## 6. Weryfikacja

Testy uruchamia się z katalogu głównego projektu:

```text
python src/tests/test_manager.py
python src/tests/test_models.py
python src/tests/test_database1.py
```

`src/tests/test_database1.py` sprawdza dwie tabele, klucz obcy, kaskadowe usuwanie, migrację JSON, ochronę przed SQL Injection, filtry i białą listę sortowania, dwa raporty JOIN, oddzielne dane bohaterów oraz rollback transferu, który przekracza udźwig. Testy migracji używają tymczasowych plików, więc nie zmieniają właściwego zapisu gry. `test_manager.py` sprawdza polimorficzną moc i limit wagi, zapis i odczyt typów przedmiotów oraz integralność bazy.

`test_models.py` sprawdza walidację przedmiotów, sortowanie, dziedziczenie i odtworzenie ekwipunku z serializacji.
