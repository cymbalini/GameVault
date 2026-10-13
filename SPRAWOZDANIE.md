# Sprawozdanie z Zadania Laboratoryjnego nr [NUMER]
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Projekt:** GameVault  
**Zespół (Autorzy):**  
1. Krzysztof Nowak (nr albumu: 164853) – login Git: `cymbalini`
2. [Imię i Nazwisko Studenta 2] (nr albumu: [NUMER]) – login Git: `[LOGIN]`  
**Data oddania:** 13.10.2026  

---

## 1. Cel i Zakres Inżynierski Zadania
Podstawowa implementacja user inputa, sworzenie walidatorów, oraz tymczasowego pliku data.py

---

## 2. Architektura Rozwiązania i Struktura Modułów

* `src/data.py` – tymczasowa baza danych
* `src/validators.py` – sprawdzanie user inputa
* `src/services.py` – logika programu
* `src/main.py` – plik główny

---

## 3. Kluczowy Fragment Kodu i Uzasadnienie Inżynierskie
*(Wybrany, najważniejszy lub najciekawszy fragment kodu źródłowego zrealizowany w tym etapie – maksymalnie 15–25 linii).*

```python
def main():
    running = True
    printMenu()
    while running:
        running = handleMenuChoice("Wybierz opcję [1-5]: ")

```

**Uzasadnienie wyboru:**  
Bez pętli w main() nie mogli byśmy wykonywać więcej niż 1 rzecz w programie.

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
3. Wyswietl craftingi TODO
4. Wyswietl aktualny ekwipunek filtrowany
5. Wyjście z programu
6. test
----------------------------------------
Wybierz opcję [1-5]: 2

========================================
INVENTORY
========================================
name: cobblestone, count: 3
name: stick, count: 2
name: wood, count: 1
----------------------------------------
Wybierz opcję [1-5]: 
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
3. Wyswietl craftingi TODO
4. Wyswietl aktualny ekwipunek filtrowany
5. Wyjście z programu
6. test
----------------------------------------
Wybierz opcję [1-5]: asd
Błąd: Nieznana opcja. Wybierz wartość od 1 do 5.
Wybierz opcję [1-5]: 
```

---

## 5. Podział Pracy w Zespole
*(Precyzyjne i uczciwe rozliczenie wkładu obu członków zespołu – weryfikowane z historią commitów `git log`).*
* **Krzysztof Nowak:**
  * Odpowiedzialność za moduły: `src/...`
  * Zaimplementowane funkcjonalności: *
  * Liczba wykonanych commitów: 
* **[Imię Nazwisko Studenta 2]:**
  * Odpowiedzialność za moduły: `src/...`
  * Zaimplementowane funkcjonalności: [...]
  * Liczba wykonanych commitów: [...]
