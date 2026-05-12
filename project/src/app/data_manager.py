import json
import os

from app.exceptions import InvalidRecipeException


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

    def load_products(self) -> list:
        return self._load("products.json", [])

    def save_products(self, data: list) -> None:
        self._save("products.json", data)

    def load_ingredients(self) -> list:
        return self._load("ingredients.json", [])

    def save_ingredients(self, data: list) -> None:
        self._save("ingredients.json", data)

    def load_recipes(self) -> dict:
        data = self._load("recipes.json", {})
        if not isinstance(data, dict):
            raise InvalidRecipeException("recipes.json 형식 오류: dict여야 합니다")
        return data

    def save_recipes(self, data: dict) -> None:
        self._save("recipes.json", data)

    def load_options(self) -> list:
        return self._load("options.json", [])

    def save_options(self, data: list) -> None:
        self._save("options.json", data)

    def load_change_reserve(self) -> dict:
        return self._load("change_reserve.json", {})

    def save_change_reserve(self, data: dict) -> None:
        self._save("change_reserve.json", data)

    # --- 통계 (dead code: 현재 미사용) ---
    # def load_stats(self) -> dict:
    #     return self._load("stats.json", {})

    # def save_stats(self, data: dict) -> None:
    #     self._save("stats.json", data)

    def load_admin_config(self) -> dict:
        return self._load("admin_config.json", {})

    def save_admin_config(self, data: dict) -> None:
        self._save("admin_config.json", data)
