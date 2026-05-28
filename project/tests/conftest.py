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
from app.drug_controller import DrugController
from app.medicine import Medicine
from app.payment import ChangeReserve
from app.symptom import Symptom, SymptomGroup


# ── QApplication (session 스코프: 한 번만 생성) ───────────────────────────
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


# ── 도메인 객체 ─────────────────────────────────────────────────────────────
@pytest.fixture
def sample_medicines():
    return [
        Medicine("m1", "타이레놀", 3000, True,  ["두통", "발열"], "해열진통제", "1회 1정", "과다복용 주의"),
        Medicine("m2", "판콜에이", 5000, True,  ["감기", "기침"], "종합감기약", "1회 2정", "졸음 주의"),
        Medicine("m3", "게보린",   2500, False, ["두통"],          "진통제",     "1회 1정", "공복 복용 금지"),
    ]


@pytest.fixture
def sample_symptoms():
    return [
        Symptom("s1", "두통",     is_emergency=False),
        Symptom("s2", "감기",     is_emergency=False),
        Symptom("s3", "심한 흉통", is_emergency=True),
    ]


@pytest.fixture
def sample_symptom_group(sample_symptoms):
    return SymptomGroup(sample_symptoms)


@pytest.fixture
def mock_dm(sample_medicines, sample_symptom_group):
    dm = MagicMock(spec=DataManager)
    dm.load_medicines.return_value = sample_medicines
    dm.load_symptoms.return_value = sample_symptom_group
    dm.load_admin_config.return_value = {"password": "1234"}
    dm.load_change_reserve.return_value = {50000: 5, 10000: 10, 5000: 20, 1000: 50}
    return dm


@pytest.fixture
def controller(mock_dm):
    return DrugController(mock_dm)


@pytest.fixture
def cart():
    return Cart()


@pytest.fixture
def change_reserve():
    return ChangeReserve({50000: 5, 10000: 10, 5000: 20, 1000: 50})


@pytest.fixture
def mock_window(controller, cart, change_reserve):
    """KioskWindow 대신 MagicMock. controller/cart/change_reserve는 실제 객체."""
    win = MagicMock()
    win.controller = controller
    win.cart = cart
    win.change_reserve = change_reserve
    win._active_payment = None
    win._current_symptom_name = None
    return win
