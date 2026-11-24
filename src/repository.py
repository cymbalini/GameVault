from data import SQLiteStorage
from src.models import HeroInventoryManager, Item


class GameRepository:

    def __init__(self, storage=None, max_weight_kg=200):
        self.storage = storage or SQLiteStorage()
        self.max_weight_kg = float(max_weight_kg)
        self.active_inventory_id = 1

    def getHeroes(self):
        heroes = self.storage.get_heroes()
        if not heroes:
            self.storage.load()
            heroes = self.storage.get_heroes()
        return heroes

    def createHero(self, character_name, max_weight_kg):
        self.getHeroes()
        return self.storage.create_hero(character_name, max_weight_kg)

    def selectHero(self, inventory_id):
        inventory_id = int(inventory_id)
        heroes = self.getHeroes()
        if not any(hero["inventory_id"] == inventory_id for hero in heroes):
            raise ValueError(f"Nie znaleziono bohatera o ID {inventory_id}.")
        self.active_inventory_id = inventory_id
        return next(hero for hero in heroes if hero["inventory_id"] == inventory_id)

    def getNextItemId(self):
        return self.storage.get_next_item_id()

    def getInventory(self):
        state = self.storage.load(self.active_inventory_id)
        inventory = HeroInventoryManager(
            state.get("max_weight_kg", self.max_weight_kg)
        )
        next_id = 0
        used_ids = set()
        reserved_ids = set()

        for saved_item in state.get("inventory", []):
            if type(saved_item) is dict:
                try:
                    old_id = saved_item.get("item_id", saved_item.get("id"))
                    if old_id is not None:
                        reserved_ids.add(int(old_id))
                except (TypeError, ValueError):
                    continue

        for saved_item in state.get("inventory", []):
            try:
                count = int(saved_item.get("count", 1))
                if count < 1:
                    continue
                stored_id = int(saved_item.get("item_id", saved_item.get("id", next_id)))

                for item_number in range(count):
                    if item_number == 0 and stored_id not in used_ids:
                        item_id = stored_id
                    else:
                        item_id = next_id
                        while item_id in used_ids or item_id in reserved_ids:
                            item_id += 1

                    item_data = {
                        "item_id": item_id,
                        "name": saved_item["name"],
                        "weight_kg": saved_item.get("weight_kg", saved_item.get("weight")),
                        "gold_value": saved_item.get("gold_value", saved_item.get("value")),
                        "rarity": self._convert_rarity(saved_item["rarity"]),
                        "type": saved_item.get("type", saved_item.get("item_type", "other")),
                    }
                    for field in (
                        "damage", "base_damage", "hit_multiplier", "durability_percent",
                        "defense", "defense_class", "equipment_slot", "magic_resistance",
                        "healing_power"
                    ):
                        if field in saved_item:
                            item_data[field] = saved_item[field]
                    item = Item.from_dict(item_data)
                    inventory.add_item(item)
                    used_ids.add(item_id)
                    next_id = max(next_id, item_id + 1)
            except (AttributeError, KeyError, TypeError, ValueError):
                print("Pominięto niepoprawny lub zbyt ciężki przedmiot w zapisie.")
        return inventory

    def _convert_rarity(self, rarity):
        rarity = str(rarity).title()
        if rarity == "Uncommon":
            return "Common"
        return rarity

    def getItems(self):
        return self.getInventory().items

    def addItem(self, item):
        inventory = self.getInventory()
        inventory.add_item(item)

        state = self.storage.load(self.active_inventory_id)
        state["inventory"] = [saved_item.to_dict() for saved_item in inventory.items]
        self.storage.save(state, inventory_id=self.active_inventory_id)

    def getGold(self):
        return self.storage.load(self.active_inventory_id).get("gold", 0)

    def addGold(self, amount):
        state = self.storage.load(self.active_inventory_id)
        state["gold"] = max(0, state.get("gold", 0) + amount)
        self.storage.save(state, inventory_id=self.active_inventory_id)
        return state["gold"]

    def sellAllItems(self):
        items = self.getItems()
        if not items:
            return 0, 0, self.getGold()

        total_value = sum(item.calculate_gold_value() for item in items)

        state = self.storage.load(self.active_inventory_id)
        state["inventory"] = []
        state["gold"] = state.get("gold", 0) + total_value
        self.storage.save(state, inventory_id=self.active_inventory_id)
        return len(items), total_value, state["gold"]

    def getWeight(self):
        return self.getInventory().total_weight_kg

    def getInventoryStatistics(self):
        return self.storage.get_inventory_statistics(self.active_inventory_id)

    def recover(self):
        return self.storage.recover()
