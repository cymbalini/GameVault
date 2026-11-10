import csv
from pathlib import Path

class CsvExporter:

    def __init__(self, file_path="exports/loot_table.csv"):
        self.file_path = Path(file_path)
        if not self.file_path.is_absolute():
            self.file_path = Path(__file__).resolve().parent / self.file_path

    def export(self, items):
        if not items:
            print("Ekwipunek jest pusty, nic do wyeksportowania.")
            return

        sorted_items = sorted(items, key=lambda item: item.calculate_gold_value())
        rows = [item.to_dict() for item in sorted_items]
        fieldnames = []
        for row in rows:
            for field in row:
                if field not in fieldnames:
                    fieldnames.append(field)

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print("Eksport CSV zakonczony pomyslnie.")
