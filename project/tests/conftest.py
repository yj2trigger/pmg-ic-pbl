"""공통 fixture — GUI 테스트는 QT_QPA_PLATFORM=offscreen 환경에서 실행됩니다."""
import os
import sys
from unittest.mock import MagicMock

import pytest

# CI 환경 / 디스플레이 없는 환경을 위한 offscreen 렌더러 설정
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# src 경로를 import path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from PyQt6.QtWidgets import QApplication

from app.cart import Cart
from app.data_manager import DataManager
from app.ingredient import Ingredient
from app.kiosk_controller import KioskController
from app.payment import ChangeReserve
from app.product import Coffee, CustomOption, Gummy, OptionGroup


# ── QApplication (session 스코프: 한 번만 생성) ───────────────
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


# ── 도메인 객체 ───────────────────────────────────────────────
@pytest.fixture
def sample_products():
    return [
        Coffee("c1", "아메리카노", 3000),
        Coffee("c2", "라떼", 3500),
        Gummy("g1", "영양구미", 2000),
    ]


@pytest.fixture
def sample_ingredients():
    return {
        "bean":   Ingredient("bean",   "원두",      2000, 5000,  "g"),
        "ice":    Ingredient("ice",    "얼음",      3000, 10000, "g"),
        "syrup":  Ingredient("syrup",  "시럽",      1500, 3000,  "ml"),
        "g_base": Ingredient("g_base", "구미베이스", 1000, 3000,  "g"),
        "vit_c":  Ingredient("vit_c",  "비타민C",   500,  1000,  "g"),
        "pouch":  Ingredient("pouch",  "파우치",    200,  500,   "개"),
    }


@pytest.fixture
def sample_option_groups():
    return [
        OptionGroup("size", "크기", [
            CustomOption("size_s", "Small",  0,   {"bean": 1}),
            CustomOption("size_m", "Medium", 300, {"bean": 2}),
        ], active_for=["coffee"]),
        OptionGroup("temperature", "온도", [
            CustomOption("temp_hot", "HOT", 0, {}),
            CustomOption("temp_ice", "ICE", 0, {"ice": 3}),
        ], active_for=["coffee"]),
        OptionGroup("shot", "샷", [
            CustomOption("shot_1", "1샷", 0,   {}),
            CustomOption("shot_2", "2샷", 300, {"bean": 1}),
        ], active_for=["coffee"]),
        OptionGroup("sweetness", "당도", [
            CustomOption("sweet_none", "없음", 0,   {}),
            CustomOption("sweet_mid",  "보통", 0,   {"syrup": 1}),
        ], active_for=["coffee"]),
        OptionGroup("flavor", "맛", [
            CustomOption("flv_straw", "딸기", 0, {"g_base": 1}),
            CustomOption("flv_grape", "포도", 0, {"g_base": 1}),
        ], active_for=["gummy"]),
        OptionGroup("effect", "성분", [
            CustomOption("eff_vitc",  "비타민C", 0, {"vit_c": 1}),
        ], active_for=["gummy"]),
        OptionGroup("count", "수량(알)", [
            CustomOption("cnt_5",  "5알",  0,   {"g_base": 1}),
            CustomOption("cnt_10", "10알", 500, {"g_base": 2}),
        ], active_for=["gummy"]),
        OptionGroup("package", "패키지", [
            CustomOption("pkg_solo",  "낱개",   0,   {}),
            CustomOption("pkg_pouch", "파우치", 300, {"pouch": 1}),
        ], active_for=["gummy"]),
    ]


@pytest.fixture
def controller(sample_products, sample_ingredients, sample_option_groups):
    return KioskController(
        products=sample_products,
        ingredients=sample_ingredients,
        option_groups=sample_option_groups,
        cart=Cart(),
        change_reserve=ChangeReserve({1000: 100, 5000: 20, 10000: 10, 50000: 5}),
        admin_config={"password": "1234"},
        data_manager=MagicMock(spec=DataManager),
    )


@pytest.fixture
def mock_window(controller):
    """KioskWindow 대신 MagicMock을 사용. controller는 실제 객체."""
    win = MagicMock()
    win.controller = controller
    return win
