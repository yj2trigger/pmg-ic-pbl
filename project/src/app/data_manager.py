# ──────────────────────────────────────────────────────────────────────────────
# data_manager.py — JSON 기반 영속성 계층
#
# [역할]
#   모든 JSON 파일 읽기·쓰기를 단일 클래스로 캡슐화한다.
#   도메인 객체(IceCreamProduct, Ingredient, OptionGroup)를 직접 생성해 반환한다.
#
# [저장 파일 목록]
#   products.json       — 상품 목록 (IceCreamProduct)
#   ingredients.json    — 재료 재고 (Ingredient)
#   options.json        — 옵션 그룹/옵션 정의 (OptionGroup, 읽기 전용)
#   change_reserve.json — 잔돈 보유 현황 {"권종": 장수}
#   admin_config.json   — 관리자 설정 {"password": "scrypt$..."}
#
# [내부 구조]
#   _save()/_load(): 공통 파일 I/O. 모든 public save*/load* 메서드가 위임.
#   경로 결정은 main.py의 DATA_DIR에서 받아 __init__에서 고정.
#
# [의존성]
#   import: json, os, ice_cream, ingredient, option
#   이 파일을 사용하는 곳:
#     main.py → DataManager(DATA_DIR) 인스턴스 생성 후 kiosk_controller에 전달
#     kiosk_controller.py → _save_after_payment(), _save_ingredients() 등
# ──────────────────────────────────────────────────────────────────────────────

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
