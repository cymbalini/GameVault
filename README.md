# GameVault

Konsolowy menedżer ekwipunku bohatera RPG. Projekt używa klas `Item`, `Weapon` i `Armor`, menedżera ekwipunku oraz bazy SQLite.

## Uruchomienie

Z katalogu głównego projektu:

```text
python src/main.py
```

Przy pierwszym uruchomieniu zapis `src/data/inventory.json` zostanie przeniesiony do tabel `inventories` i `inventory_items` w `src/data/gamevault.db`. Plik JSON zostanie zachowany jako `src/data/inventory.json.bak`. SQLite jest częścią biblioteki standardowej Pythona, więc nie trzeba instalować osobnego serwera ani pakietu. Kopia bazy jest zapisywana w `src/data/backup/gamevault.db.bak`.

## Testy

```text
python src/tests/test_manager.py
python src/tests/test_models.py
python src/tests/test_database.py
```

Opcja 11 w menu pokazuje podsumowanie przedmiotów według rzadkości. Dane są liczone w SQLite przez `JOIN`, `GROUP BY`, `SUM` i `AVG`. Wartości w zapytaniach SQL są przekazywane przez placeholdery `?`.
