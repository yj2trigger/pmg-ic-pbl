import json
import os

from app.ice_cream import IceCreamProduct
from app.ingredient import Ingredient
from app.option import OptionGroup


class DataManager:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def _path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)

    def _load(self, filename: str, default):
        path = self._path(filename)
        if not os.path.exists(path):
            return default
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, filename: str, data) -> None:
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self._path(filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_products(self) -> list[IceCreamProduct]:
        raw = self._load("products.json", [])
        return [IceCreamProduct(**item) for item in raw]

    def save_products(self, products: list[IceCreamProduct]) -> None:
        data = [
            {
                "product_id": p.product_id,
                "name": p.name,
                "base_price": p.base_price,
                "is_available": p.is_available,
                "product_type": p.product_type,
            }
            for p in products
        ]
        self._save("products.json", data)

    def load_ingredients(self) -> dict[str, Ingredient]:
        raw = self._load("ingredients.json", [])
        return {item["ingredient_id"]: Ingredient(**item) for item in raw}

    def save_ingredients(self, ingredients_list: list) -> None:
        self._save("ingredients.json", ingredients_list)

    def load_option_groups(self) -> list[OptionGroup]:
        raw = self._load("options.json", [])
        return [OptionGroup(**item) for item in raw]

    def load_change_reserve(self) -> dict:
        return self._load("change_reserve.json", {})

    def save_change_reserve(self, data: dict) -> None:
        self._save("change_reserve.json", data)

    def load_admin_config(self) -> dict:
        return self._load("admin_config.json", {})

    def save_admin_config(self, data: dict) -> None:
        self._save("admin_config.json", data)
