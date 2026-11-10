# Sprawozdanie z Zadania 3 – GameVault

**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Temat:** Dziedziczenie, polimorfizm i menedżer ekwipunku  
**Autor:** Krzysztof Nowak  
**Data:** 10.11.2026

---

## 1. Cel zadania

Projekt GameVault został rozbudowany o abstrakcyjną hierarchię przedmiotów RPG. Wspólna klasa bazowa określa kontrakt przedmiotu, podklasy obliczają własny potencjał bojowy, a menedżer zarządza ekwipunkiem i jego udźwigiem. Program zapisuje i odtwarza typy przedmiotów w JSON, eksportuje CSV oraz pozwala sprzedać cały ekwipunek.

## 2. Struktura programu

* `src/models/Item.py` – abstrakcyjna klasa bazowa `Item`, wspólne dane i kontrakt mocy bojowej.
* `src/models/Weapon.py` – broń z obrażeniami, mnożnikiem trafienia i trwałością.
* `src/models/Armor.py` – pancerz z klasą obrony, slotem i odpornością na magię.
* `src/models/Potion.py` – mikstura z siłą leczenia.
* `src/models/MiscItem.py` – zwykłe przedmioty, w tym starsze wpisy zapisane jako `Item`.
* `src/models/Inventory.py` – `HeroInventoryManager` oraz zachowana nazwa `Inventory` dla testów modeli.
* `src/models/__init__.py` – rejestr klas używany przy odtwarzaniu obiektów z JSON.
* `src/repository.py` – `GameRepository`, który oddziela operacje na ekwipunku i złocie od menu.
* `src/data.py` – `JsonStorage`, zapis atomowy, kopie zapasowe i kontrola sumy złota.
* `src/CsvExporter.py` – eksport przedmiotów o różnych polach do CSV.
* `src/validators.py` i `src/services.py` – walidacja wejścia i obsługa CLI.
* `src/tests/test_manager.py` – testy menedżera wymagane w bieżącym etapie.
* `src/tests/test_models.py` – dodatkowe testy modeli.

## 3. Hierarchia klas i polimorfizm

```text
Item (ABC)
├── Weapon
├── Armor
├── Potion
└── MiscItem
```

`Item` przechowuje `item_id`, `name`, `weight_kg`, `gold_value` i `rarity`. Rzadkość musi być jedną z wartości `Common`, `Rare`, `Epic` lub `Legendary`. Klasa bazowa wymaga implementacji `calculate_effective_power()`.

`Weapon` oblicza moc na podstawie obrażeń, mnożnika trafienia i trwałości. `Armor` uwzględnia klasę obrony i odporność na magię. `Potion` używa siły leczenia, a `MiscItem` zwraca moc równą zero. `HeroInventoryManager` sumuje wynik przez wywołanie tej samej metody na każdym elemencie kolekcji, bez rozpoznawania jego konkretnej klasy.

Menedżer pilnuje limitu `max_weight_kg` w `add_item()`. Po przekroczeniu limitu zgłasza `ValueError` i nie zmienia ekwipunku. Udostępnia również filtrowanie, sortowanie, obliczanie sumarycznej mocy oraz serializację kolekcji.

## 4. Menedżer i persystencja

`GameRepository` przekazuje operacje między CLI a `HeroInventoryManager` i `JsonStorage`. Warstwa menu nie zarządza bezpośrednio słownikami JSON. Eksport CSV zbiera kolumny ze wszystkich przedmiotów, więc broń, pancerz i mikstura mogą mieć własne pola.

JSON zapisuje dyskryminator w polu `type`, na przykład `weapon` albo `armor`. `ITEM_REGISTRY` wybiera klasę podczas `Item.from_dict()`, a `to_dict()` zapisuje pola specyficzne dla podklasy. Wczytywanie obsługuje również wcześniejsze wpisy z `item_type`, `damage` i `defense`.

Opcja 10 menu sprzedaje cały ekwipunek. Menedżer/repozytorium sumuje wycenę przedmiotów, dodaje ją do złota i zapisuje pusty plecak z kopią poprzedniego stanu.

## 5. Kluczowy fragment

```python
@abstractmethod
def calculate_effective_power(self) -> float:
    pass

def calculate_total_combat_power(self) -> float:
    return sum(item.calculate_effective_power() for item in self._items)
```

Klasa bazowa wymusza wspólną metodę, a menedżer oblicza wynik całej kolekcji przez polimorfizm. Dodanie nowej podklasy nie wymaga dopisywania warunków typów w menedżerze.

## 6. Testy i weryfikacja

Testy można uruchomić z katalogu głównego projektu:

```text
python src/tests/test_manager.py
python src/tests/test_models.py
```

`test_manager.py` sprawdza sumowanie mocy różnych podklas, odrzucenie przedmiotu przekraczającego udźwig, odtworzenie typów z serializacji i abstrakcyjność `Item`. `test_models.py` sprawdza także walidację, sortowanie i round-trip ekwipunku.

Oba zestawy testów uruchomiono pomyślnie. Sprawdzono również eksport mieszanej listy typów oraz sprzedaż całego ekwipunku.

## 7. Podział Pracy w Zespole
*(Precyzyjne i uczciwe rozliczenie wkładu obu członków zespołu – weryfikowane z historią commitów `git log`).*
* **Krzysztof Nowak:**
  * Odpowiedzialność za moduły: `src/...`
  * Zaimplementowane funkcjonalności: *
  * Liczba wykonanych commitów: * 
