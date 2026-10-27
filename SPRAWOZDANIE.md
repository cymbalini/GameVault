# Sprawozdanie z Zadania Laboratoryjnego nr 3
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Projekt:** GameVault  
**Zespół (Autorzy):**  
1. Krzysztof Nowak (nr albumu: 164853) – login Git: `cymbalini`
**Data oddania:** 27.10.2026  

---

## 1. Cel i Zakres Inżynierski Zadania
* zapis atomowy oraz tworzenie i odzyskiwanie backupow
---

## 2. Architektura Rozwiązania i Struktura Modułów

* `src/data.py` – tymczasowa baza danych
* `src/validators.py` – sprawdzanie user inputa
* `src/services.py` – logika programu
* `src/main.py` – plik główny
* `src/data` - pliki json oraz export csv oraz backupy

---

## 3. Kluczowy Fragment Kodu i Uzasadnienie Inżynierskie
*(Wybrany, najważniejszy lub najciekawszy fragment kodu źródłowego zrealizowany w tym etapie – maksymalnie 15–25 linii).*

```python
def generate_gold_hash(gold_value: int) -> str:
    return hashlib.sha256(f"{gold_value}{SECRET_SALT}".encode('utf-8')).hexdigest()

```

**Uzasadnienie wyboru:**  
hashowanie jest wazne by nikt nie mogl swobodnie zmieniac zlota w plecaku

---

## 4. Scenariusze Weryfikacji i Wyniki Testów
*(Dowód działania programu w konsoli. Należy przedstawić przynajmniej dwa scenariusze).*

### Scenariusz A: Ścieżka poprawna (Happy Path)
* **Dane wejściowe:** 2
* **Oczekiwany i uzyskany wynik:** posiadanie i wyswietlenie pliku savegames
```text
Wybierz opcję [1-7]: 2

========================================
INVENTORY
========================================
---------------------------------------------------------------------------------------------------------
|name                |count               |weight              |rarity              |value               |
---------------------------------------------------------------------------------------------------------
|a                   |2                   |12.0                |common              |12.0                |
---------------------------------------------------------------------------------------------------------
total 24.0 of weight points in inventory.
Wybierz opcję [1-7]: 
```

### Scenariusz B: Obsługa błędów i wartości brzegowych
* **Dane wejściowe (błędne): 2 i brak pliku savegames
* **Reakcja programu:** 
```text
========================================
 SYSTEM ZARZĄDZANIA KAWIARNIĄ GameVault
========================================
1. Wyświetl aktualne menu
2. Wyswietl aktualny ekwipunek
3. Wyswietl filtrowany ekwipunek przez rzadkosc
4. Wyswietl aktualny ekwipunek filtrowany przez kategorie
5. Dodaj item
6. Eksport danych do csv
7. Wyjście z programu
----------------------------------------
Wybierz opcję [1-7]: 2
Brak pliku zapisu JSON.
Tworzenie pustej bazy danych.

========================================
INVENTORY
========================================
---------------------------------------------------------------------------------------------------------
|name                |count               |weight              |rarity              |value               |
---------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------
total 0.0 of weight points in inventory.

```

---

## 5. Podział Pracy w Zespole
*(Precyzyjne i uczciwe rozliczenie wkładu obu członków zespołu – weryfikowane z historią commitów `git log`).*
* **Krzysztof Nowak:**
  * Odpowiedzialność za moduły: `src/...`
  * Zaimplementowane funkcjonalności: *
  * Liczba wykonanych commitów: *

