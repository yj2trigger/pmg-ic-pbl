import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
from app.data_manager import DataManager
from app.product import Coffee, Gummy, CustomOption, OptionGroup
from app.ingredient import Ingredient
from app.cart import Cart
from app.payment import ChangeReserve
from app.kiosk_controller import KioskController
from app.cli_view import CLIView

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ── 기본 데이터 정의 ────────────────────────────────────────────
DEFAULT_PRODUCTS = [
    {"product_id": "c1", "name": "아메리카노", "base_price": 3000, "product_type": "coffee", "is_available": True},
    {"product_id": "c2", "name": "라떼",       "base_price": 3500, "product_type": "coffee", "is_available": True},
    {"product_id": "c3", "name": "카푸치노",   "base_price": 3500, "product_type": "coffee", "is_available": True},
    {"product_id": "g1", "name": "영양구미",   "base_price": 2000, "product_type": "gummy",  "is_available": True},
]

DEFAULT_INGREDIENTS = [
    {"ingredient_id": "bean",    "name": "원두",      "stock": 2000, "max_capacity": 5000,  "unit": "g"},
    {"ingredient_id": "milk",    "name": "우유",      "stock": 5000, "max_capacity": 10000, "unit": "ml"},
    {"ingredient_id": "ice",     "name": "얼음",      "stock": 3000, "max_capacity": 10000, "unit": "g"},
    {"ingredient_id": "cream",   "name": "크림",      "stock": 800,  "max_capacity": 2000,  "unit": "ml"},
    {"ingredient_id": "syrup",   "name": "시럽",      "stock": 1500, "max_capacity": 3000,  "unit": "ml"},
    {"ingredient_id": "g_base",  "name": "구미베이스", "stock": 1000, "max_capacity": 3000,  "unit": "g"},
    {"ingredient_id": "vit_c",   "name": "비타민C",   "stock": 500,  "max_capacity": 1000,  "unit": "g"},
    {"ingredient_id": "omega3",  "name": "오메가3",   "stock": 500,  "max_capacity": 1000,  "unit": "g"},
    {"ingredient_id": "collagen","name": "콜라겐",    "stock": 500,  "max_capacity": 1000,  "unit": "g"},
    {"ingredient_id": "pouch",   "name": "파우치",    "stock": 200,  "max_capacity": 500,   "unit": "개"},
]

DEFAULT_OPTIONS = [
    # 커피 공통
    {"group_id": "size", "name": "크기", "active_for": ["coffee"], "options": [
        {"option_id": "size_s", "name": "Small",  "extra_price": 0,   "required_ingredients_dic": {"bean": 1}},
        {"option_id": "size_m", "name": "Medium", "extra_price": 300, "required_ingredients_dic": {"bean": 2}},
        {"option_id": "size_l", "name": "Large",  "extra_price": 500, "required_ingredients_dic": {"bean": 3}},
    ]},
    {"group_id": "temperature", "name": "온도", "active_for": ["coffee"], "options": [
        {"option_id": "temp_hot", "name": "HOT", "extra_price": 0, "required_ingredients_dic": {}},
        {"option_id": "temp_ice", "name": "ICE", "extra_price": 0, "required_ingredients_dic": {"ice": 3}},
    ]},
    {"group_id": "shot", "name": "샷", "active_for": ["coffee"], "options": [
        {"option_id": "shot_1", "name": "1샷", "extra_price": 0,   "required_ingredients_dic": {}},
        {"option_id": "shot_2", "name": "2샷", "extra_price": 300, "required_ingredients_dic": {"bean": 1}},
    ]},
    {"group_id": "sweetness", "name": "당도", "active_for": ["coffee"], "options": [
        {"option_id": "sweet_none", "name": "없음", "extra_price": 0,   "required_ingredients_dic": {}},
        {"option_id": "sweet_mid",  "name": "보통", "extra_price": 0,   "required_ingredients_dic": {"syrup": 1}},
        {"option_id": "sweet_high", "name": "많이", "extra_price": 200, "required_ingredients_dic": {"syrup": 2}},
    ]},
    {"group_id": "cream", "name": "크림", "active_for": ["latte", "cappuccino"], "options": [
        {"option_id": "cream_yes", "name": "있음", "extra_price": 200, "required_ingredients_dic": {"cream": 1, "milk": 1}},
        {"option_id": "cream_no",  "name": "없음", "extra_price": 0,   "required_ingredients_dic": {}},
    ]},
    # 구미
    {"group_id": "flavor", "name": "맛", "active_for": ["gummy"], "options": [
        {"option_id": "flv_straw", "name": "딸기", "extra_price": 0,   "required_ingredients_dic": {"g_base": 1}},
        {"option_id": "flv_grape", "name": "포도", "extra_price": 0,   "required_ingredients_dic": {"g_base": 1}},
        {"option_id": "flv_lemon", "name": "레몬", "extra_price": 200, "required_ingredients_dic": {"g_base": 1}},
    ]},
    {"group_id": "effect", "name": "성분", "active_for": ["gummy"], "options": [
        {"option_id": "eff_vitc",  "name": "비타민C",  "extra_price": 0,   "required_ingredients_dic": {"vit_c": 1}},
        {"option_id": "eff_omega", "name": "오메가3",  "extra_price": 300, "required_ingredients_dic": {"omega3": 1}},
        {"option_id": "eff_col",   "name": "콜라겐",   "extra_price": 500, "required_ingredients_dic": {"collagen": 1}},
    ]},
    {"group_id": "count", "name": "수량(알)", "active_for": ["gummy"], "options": [
        {"option_id": "cnt_5",  "name": "5알",  "extra_price": 0,    "required_ingredients_dic": {"g_base": 1}},
        {"option_id": "cnt_10", "name": "10알", "extra_price": 500,  "required_ingredients_dic": {"g_base": 2}},
        {"option_id": "cnt_20", "name": "20알", "extra_price": 1000, "required_ingredients_dic": {"g_base": 4}},
    ]},
    {"group_id": "package", "name": "패키지", "active_for": ["gummy"], "options": [
        {"option_id": "pkg_solo",  "name": "낱개",   "extra_price": 0,   "required_ingredients_dic": {}},
        {"option_id": "pkg_pouch", "name": "파우치", "extra_price": 300, "required_ingredients_dic": {"pouch": 1}},
    ]},
]

DEFAULT_CHANGE_RESERVE = {"50000": 5, "10000": 10, "5000": 20, "1000": 50}
DEFAULT_ADMIN_CONFIG   = {"password": "1234"}


# ── 빌더 함수들 ────────────────────────────────────────────────
def _build_products(data: list) -> list:
    result = []
    for d in data:
        cls = Coffee if d["product_type"] == "coffee" else Gummy
        result.append(cls(d["product_id"], d["name"], d["base_price"],
                          d.get("is_available", True)))
    return result


def _build_ingredients(data: list) -> dict:
    return {
        d["ingredient_id"]: Ingredient(
            d["ingredient_id"], d["name"], d["stock"], d["max_capacity"],
            d.get("unit", "개"),
        )
        for d in data
    }


def _build_option_groups(data: list) -> list:
    groups = []
    for g in data:
        options = [
            CustomOption(
                o["option_id"], o["name"],
                o.get("extra_price", 0),
                o.get("required_ingredients_dic", {}),
            )
            for o in g["options"]
        ]
        groups.append(OptionGroup(
            g["group_id"], g["name"], options,
            active_for=g.get("active_for", []),
        ))
    return groups


def _build_change_reserve(data: dict) -> ChangeReserve:
    return ChangeReserve({int(k): v for k, v in data.items()})


# ── 진입점 ──────────────────────────────────────────────────────
def main():
    dm = DataManager(DATA_DIR)

    # 파일 없으면 기본값으로 초기화
    if not dm.load_products():
        dm.save_products(DEFAULT_PRODUCTS)
    if not dm.load_ingredients():
        dm.save_ingredients(DEFAULT_INGREDIENTS)
    if not dm.load_options():
        dm.save_options(DEFAULT_OPTIONS)
    if not dm.load_change_reserve():
        dm.save_change_reserve(DEFAULT_CHANGE_RESERVE)
    if not dm.load_admin_config():
        dm.save_admin_config(DEFAULT_ADMIN_CONFIG)

    products      = _build_products(dm.load_products())
    ingredients   = _build_ingredients(dm.load_ingredients())
    option_groups = _build_option_groups(dm.load_options())
    change_reserve = _build_change_reserve(dm.load_change_reserve())
    admin_config  = dm.load_admin_config()

    controller = KioskController(
        products=products,
        ingredients=ingredients,
        option_groups=option_groups,
        cart=Cart(),
        change_reserve=change_reserve,
        admin_config=admin_config,
        data_manager=dm,
    )
    CLIView(controller).run()


if __name__ == "__main__":
    main()
