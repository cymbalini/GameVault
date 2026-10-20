# Sprawozdanie z Zadania Laboratoryjnego nr 2
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Projekt:** GameVault  
**Zespół (Autorzy):**  
1. Krzysztof Nowak (nr albumu: 164853) – login Git: `cymbalini`
2. [Imię i Nazwisko Studenta 2] (nr albumu: [NUMER]) – login Git: `[LOGIN]`  
**Data oddania:** 13.10.2026  

---

## 1. Cel i Zakres Inżynierski Zadania
* przetwarzanie danych przy pomocy json oraz export do csv
---

## 2. Architektura Rozwiązania i Struktura Modułów

* `src/data.py` – tymczasowa baza danych
* `src/validators.py` – sprawdzanie user inputa
* `src/services.py` – logika programu
* `src/main.py` – plik główny
* `src/data` - pliki json oraz export csv

---

## 3. Kluczowy Fragment Kodu i Uzasadnienie Inżynierskie
*(Wybrany, najważniejszy lub najciekawszy fragment kodu źródłowego zrealizowany w tym etapie – maksymalnie 15–25 linii).*

```python
def getInventory() -> list:
    try:
        with open('data/inventory.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print('Inventory file not found, creating new one')
        open('data/inventory.json', 'w')
        return []
    except PermissionError:
        print('Missing permissions')
        return []
    except json.decoder.JSONDecodeError:
        print('JSON decode error')
        return []
```

**Uzasadnienie wyboru:**  
duza ilosc except

---

## 4. Scenariusze Weryfikacji i Wyniki Testów
*(Dowód działania programu w konsoli. Należy przedstawić przynajmniej dwa scenariusze).*

### Scenariusz A: Ścieżka poprawna (Happy Path)
* **Dane wejściowe:** 2
* **Oczekiwany i uzyskany wynik:** chcieliśmy wyświetlić aktualy ekwipunek. Wyświetlim nam się on.
```text
========================================
 SYSTEM ZARZĄDZANIA KAWIARNIĄ GameVault
========================================
1. Wyświetl aktualne menu
2. Wyswietl aktualny ekwipunek
3. Wyswietl filtrowany ekwipunek przez rzadkosc
4. Wyswietl aktualny ekwipunek filtrowany przez kategorie
5. Dodaj item
6. test
7. Wyjście z programu
----------------------------------------
Wybierz opcję [1-5]: 6
```

### Scenariusz B: Obsługa błędów i wartości brzegowych
* **Dane wejściowe (błędne): asd
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
6. test
7. Wyjście z programu
----------------------------------------
Wybierz opcję [1-5]: sa
Błąd: Nieznana opcja. Wybierz wartość od 1 do 5.
Wybierz opcję [1-5]: 
```

---

## 5. Podział Pracy w Zespole
*(Precyzyjne i uczciwe rozliczenie wkładu obu członków zespołu – weryfikowane z historią commitów `git log`).*
* **Krzysztof Nowak:**
  * Odpowiedzialność za moduły: `src/...`
  * Zaimplementowane funkcjonalności: *
  * Liczba wykonanych commitów: *

