"""공통 fixture — GUI 테스트는 QT_QPA_PLATFORM=offscreen 환경에서 실행됩니다."""
import os
import sys
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Mock audio/TTS libs so tests run without audio device or network access
for _mod in ("pygame", "pygame.mixer", "edge_tts"):
    sys.modules.setdefault(_mod, MagicMock())

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from PyQt6.QtWidgets import QApplication

from app.cart import Cart
from app.data_manager import DataManager
from app.ice_cream import IceCreamProduct
from app.kiosk_controller import KioskController
from app.payment import ChangeReserve


# ── QApplication (session 스코프: 한 번만 생성) ───────────────────────────
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


# ── 도메인 객체 ─────────────────────────────────────────────────────────────
@pytest.fixture
def sample_products():
    return [
        IceCreamProduct("p1", "스틱 아이스크림", 3000, True,  "stick"),
        IceCreamProduct("p2", "스쿱 아이스크림", 4000, True,  "scoop"),
        IceCreamProduct("p3", "품절 아이스크림", 2000, False, "stick"),
    ]


@pytest.fixture
def mock_dm(sample_products):
    dm = MagicMock(spec=DataManager)
    dm.load_products.return_value = sample_products
    dm.load_ingredients.return_value = {}
    dm.load_option_groups.return_value = []
    dm.load_admin_config.return_value = {"password": "1234"}
    dm.load_change_reserve.return_value = {50000: 5, 10000: 10, 5000: 20, 1000: 50}
    return dm


@pytest.fixture
def cart():
    return Cart()


@pytest.fixture
def change_reserve():
    return ChangeReserve({50000: 5, 10000: 10, 5000: 20, 1000: 50})


@pytest.fixture
def controller(mock_dm, sample_products, cart, change_reserve):
    admin_config = mock_dm.load_admin_config.return_value
    return KioskController(sample_products, {}, [], cart, change_reserve, admin_config, mock_dm)


@pytest.fixture
def mock_window(controller, cart, change_reserve):
    """KioskWindow 대신 MagicMock. controller/cart/change_reserve는 실제 객체."""
    win = MagicMock()
    win.controller = controller
    win.cart = cart
    win.change_reserve = change_reserve
    win._active_payment = None
    return win
