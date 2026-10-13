def getIntInput(
    prompt: str,
    min_val: int = None,
    max_val: int = None
) -> int:
    """Pobiera int z walidacją."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Błąd: Pusta wartość.")
            continue
        try:
            val = int(raw)
            if min_val is not None and val < min_val:
                print(f"Błąd: Wartość < {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"Błąd: Wartość > {max_val}")
                continue
            return val
        except ValueError:
            print(f"Błąd: '{raw}' to nie int!")

def getIntFloat(
    prompt: str,
    min_val: float = None,
    max_val: float = None
) -> float:
    """Pobiera int z walidacją."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Błąd: Pusta wartość.")
            continue
        try:
            val = float(raw)
            if min_val is not None and val < min_val:
                print(f"Błąd: Wartość < {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"Błąd: Wartość > {max_val}")
                continue
            return val
        except ValueError:
            print(f"Błąd: '{raw}' to nie float!")

def getNonEmptyString(
        prompt: str
) -> str:
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Błąd: Pusta wartość.")
            continue
        else:
            return raw


def getValidCategory(prompt: str) -> str:
    categories = ["name","id","weight","count"]
    while True:
        raw = input(prompt).strip().lower()
        if raw not in categories:
            print("podaj poprawna kategorie.")
            continue
        else:
            return raw