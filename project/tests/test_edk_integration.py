"""EDK 통합 시나리오 테스트."""
from unittest.mock import MagicMock

from app.cart import Cart, OrderItem
from app.data_manager import DataManager
from app.drug_controller import DrugController
from app.medicine import Medicine
from app.payment import CashPayment, ChangeReserve
from app.symptom import Symptom, SymptomGroup


def _make_controller(medicines, symptoms):
    dm = MagicMock(spec=DataManager)
    dm.load_medicines.return_value = medicines
    dm.load_symptoms.return_value = SymptomGroup(symptoms)
    dm.load_admin_config.return_value = {"password": "1234"}
    return DrugController(dm)


# ─── 장바구니 & 의약품 탐색 ───────────────────────────────────────────────────

class TestBrowseAndCart:

    def test_add_medicine_to_cart_and_subtotal(self):
        m = Medicine("m1", "타이레놀", 3000, True, ["두통"])
        cart = Cart()
        cart.add_item(OrderItem(m, {}, 2), {})
        assert cart.get_subtotal() == 6000

    def test_filter_medicines_by_symptom(self):
        medicines = [
            Medicine("m1", "타이레놀", 3000, True, ["두통"]),
            Medicine("m2", "판콜에이", 5000, True, ["감기"]),
        ]
        ctrl = _make_controller(medicines, [])
        result = ctrl.get_medicines_for_symptom("두통")
        assert len(result) == 1
        assert result[0].medicine_id == "m1"

    def test_get_available_medicines_excludes_unavailable(self):
        medicines = [
            Medicine("m1", "타이레놀", 3000, True,  ["두통"]),
            Medicine("m2", "게보린",   2500, False, ["두통"]),
        ]
        ctrl = _make_controller(medicines, [])
        result = ctrl.get_available_medicines()
        assert len(result) == 1
        assert result[0].medicine_id == "m1"

    def test_remove_item_from_cart(self):
        m1 = Medicine("m1", "타이레놀", 3000, True, ["두통"])
        m2 = Medicine("m2", "판콜에이", 5000, True, ["감기"])
        cart = Cart()
        cart.add_item(OrderItem(m1, {}, 1), {})
        cart.add_item(OrderItem(m2, {}, 1), {})
        cart.remove_item(0, {})
        assert len(cart.items) == 1
        assert cart.items[0].product.medicine_id == "m2"

    def test_clear_cart(self):
        m = Medicine("m1", "타이레놀", 3000, True, ["두통"])
        cart = Cart()
        cart.add_item(OrderItem(m, {}, 3), {})
        cart.clear({})
        assert cart.is_empty()


# ─── 응급 증상 ────────────────────────────────────────────────────────────────

class TestEmergencySymptom:

    def test_symptom_group_has_emergency(self):
        symptoms = [
            Symptom("s1", "두통",     is_emergency=False),
            Symptom("s2", "심한 흉통", is_emergency=True),
        ]
        group = SymptomGroup(symptoms)
        emergencies = group.get_emergency_symptoms()
        assert len(emergencies) == 1
        assert emergencies[0].name == "심한 흉통"

    def test_symptom_group_len(self):
        symptoms = [
            Symptom("s1", "두통"),
            Symptom("s2", "감기"),
            Symptom("s3", "흉통", is_emergency=True),
        ]
        group = SymptomGroup(symptoms)
        assert len(group) == 3

    def test_get_symptom_by_id(self):
        symptoms = [Symptom("s1", "두통"), Symptom("s2", "감기")]
        group = SymptomGroup(symptoms)
        assert group.get_symptom("s1").name == "두통"
        assert group.get_symptom("not_exist") is None


# ─── 현금 결제 플로우 ─────────────────────────────────────────────────────────

class TestCashPaymentFlow:

    def test_cash_payment_can_complete_after_insert(self):
        reserve = ChangeReserve({1000: 100, 5000: 20, 10000: 10})
        pmt = CashPayment(3000, reserve)
        pmt.insert(5000)
        assert pmt.can_complete()

    def test_cash_payment_insufficient_before_insert(self):
        reserve = ChangeReserve({1000: 100})
        pmt = CashPayment(3000, reserve)
        assert not pmt.can_complete()

    def test_cash_payment_change_calculated(self):
        reserve = ChangeReserve({1000: 100, 5000: 20})
        pmt = CashPayment(3000, reserve)
        pmt.insert(5000)
        assert pmt.get_change_amount() == 2000

    def test_cash_payment_process_returns_change(self):
        reserve = ChangeReserve({1000: 100, 5000: 20, 10000: 10})
        pmt = CashPayment(3000, reserve)
        pmt.insert(5000)
        change = pmt.process()
        total_change = sum(d * c for d, c in change.items())
        assert total_change == 2000


# ─── DrugController ──────────────────────────────────────────────────────────

class TestDrugController:

    def test_get_all_symptoms(self, controller):
        result = controller.get_all_symptoms()
        assert len(result) == 3

    def test_get_medicines_for_symptom(self, controller):
        result = controller.get_medicines_for_symptom("두통")
        assert all("두통" in m.symptom_categories for m in result)
        assert all(m.is_available for m in result)

    def test_get_available_medicines(self, controller):
        result = controller.get_available_medicines()
        assert all(m.is_available for m in result)
        assert len(result) == 2  # m1, m2 판매중; m3 판매중지

    def test_get_medicine_by_id_found(self, controller):
        result = controller.get_medicine_by_id("m1")
        assert result is not None
        assert result.name == "타이레놀"

    def test_get_medicine_by_id_not_found(self, controller):
        result = controller.get_medicine_by_id("nonexistent")
        assert result is None
