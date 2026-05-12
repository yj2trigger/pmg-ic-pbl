"""
20+ 예외 시나리오 통합 테스트
각 케이스는 실제 사용 중 발생 가능한 상황을 재현합니다.
"""
import unittest
import tempfile
import shutil
import json
import os

from app.ingredient import Ingredient
from app.product import Coffee, Gummy, CustomOption, OptionGroup
from app.cart import Cart, OrderItem
from app.payment import ChangeReserve, CashPayment, CardPayment
from app.data_manager import DataManager
from app.kiosk_controller import KioskController
from app.exceptions import (
    KioskException, InsufficientStockException, StockOverflowException,
    InsufficientChangeException, PaymentException,
    AdminAuthException, InvalidRecipeException,
)


# ── 헬퍼 ────────────────────────────────────────────────────────
def _ing(stock, max_cap=100):
    return Ingredient("bean", "원두", stock, max_cap)

def _reserve(d: dict):
    base = {50000: 0, 10000: 0, 5000: 0, 1000: 0}
    base.update(d)
    return ChangeReserve(base)

def _make_controller(stock=50, reserve=None, password="1234"):
    tmp = tempfile.mkdtemp()
    ing = Ingredient("bean", "원두", stock, 100)
    opt = CustomOption("size_l", "Large", 500, {"bean": 2})
    group = OptionGroup("size", "크기", [opt], active_for=["coffee"])
    products = [Coffee("p1", "아메리카노", 3000)]
    ctrl = KioskController(
        products=products,
        ingredients={"bean": ing},
        option_groups=[group],
        cart=Cart(),
        change_reserve=reserve or _reserve({10000: 5, 5000: 5, 1000: 10}),
        admin_config={"password": password},
        data_manager=DataManager(tmp),
    )
    ctrl._tmp = tmp
    ctrl._ing = ing
    return ctrl


class TestExceptionScenarios(unittest.TestCase):

    def tearDown(self):
        if hasattr(self, "ctrl"):
            shutil.rmtree(self.ctrl._tmp, ignore_errors=True)

    # ══ ValueError ══════════════════════════════════════════════

    def test_01_insert_invalid_denomination_300(self):
        """300원은 유효 권종이 아님"""
        p = CashPayment(3000, _reserve({1000: 5}))
        with self.assertRaises(ValueError):
            p.insert(300)

    def test_02_insert_denomination_zero(self):
        """0원 투입 거부"""
        p = CashPayment(3000, _reserve({1000: 5}))
        with self.assertRaises(ValueError):
            p.insert(0)

    def test_03_insert_denomination_negative(self):
        """음수 권종 거부"""
        p = CashPayment(3000, _reserve({1000: 5}))
        with self.assertRaises(ValueError):
            p.insert(-1000)

    def test_04_card_amount_negative(self):
        """결제 금액 음수 거부"""
        with self.assertRaises(ValueError):
            CardPayment(-500)

    def test_05_card_amount_float(self):
        """결제 금액 소수 거부"""
        with self.assertRaises(ValueError):
            CardPayment(3000.5)

    def test_06_card_amount_bool(self):
        """True/False는 int처럼 보이지만 거부"""
        with self.assertRaises(ValueError):
            CardPayment(True)

    def test_07_card_invalid_fail_reason(self):
        """정의되지 않은 fail_reason 거부"""
        with self.assertRaises(ValueError):
            CardPayment(3000, fail_reason="hack")

    def test_08_payment_base_negative(self):
        """Payment 기반 클래스 음수 거부 (CashPayment 경유)"""
        with self.assertRaises(ValueError):
            CashPayment(-1, _reserve({}))

    # ══ InsufficientStockException ══════════════════════════════

    def test_09_deduct_over_stock(self):
        """재고(10)보다 많이 차감 시도"""
        ing = _ing(10)
        with self.assertRaises(InsufficientStockException):
            ing.deduct(11)

    def test_10_deduct_from_zero_stock(self):
        """재고 0에서 차감 시도"""
        ing = _ing(0)
        with self.assertRaises(InsufficientStockException):
            ing.deduct(1)

    def test_11_cart_add_insufficient_stock(self):
        """장바구니 추가 시 재고 부족"""
        opt = CustomOption("o", "Large", 0, {"bean": 10})
        item = OrderItem(Coffee("p1", "아메리카노", 3000), {"size": opt}, 1)
        ing = {"bean": _ing(5)}  # 5 보유, 10 필요
        cart = Cart()
        with self.assertRaises(InsufficientStockException):
            cart.add_item(item, ing)

    def test_12_cart_add_qty2_insufficient(self):
        """수량 2개 추가 시 재고 부족 (단위×수량 검증)"""
        opt = CustomOption("o", "Large", 0, {"bean": 3})
        item = OrderItem(Coffee("p1", "아메리카노", 3000), {"size": opt}, 2)
        ing = {"bean": _ing(5)}  # 5 보유, 3×2=6 필요
        cart = Cart()
        with self.assertRaises(InsufficientStockException):
            cart.add_item(item, ing)

    def test_13_cart_update_increase_insufficient(self):
        """수량 증가 시 추가 재고 부족"""
        opt = CustomOption("o", "Large", 0, {"bean": 3})
        ing = {"bean": _ing(10)}
        cart = Cart()
        item = OrderItem(Coffee("p1", "아메리카노", 3000), {"size": opt}, 1)
        cart.add_item(item, ing)  # 3 차감 → 재고 7
        with self.assertRaises(InsufficientStockException):
            cart.update_quantity(0, 5, ing)  # 추가 3×4=12 필요, 7만 있음

    def test_14_controller_add_to_cart_no_stock(self):
        """Controller를 통한 장바구니 추가 - 재고 부족"""
        self.ctrl = _make_controller(stock=1)
        p = self.ctrl.products[0]
        opt = self.ctrl.option_groups[0].get_options()[0]  # bean: 2 필요
        with self.assertRaises(InsufficientStockException):
            self.ctrl.add_to_cart(p, {"size": opt}, 1)

    # ══ StockOverflowException ══════════════════════════════════

    def test_15_replenish_over_max(self):
        """재고 보충 시 최대 용량 초과"""
        ing = _ing(90, max_cap=100)
        with self.assertRaises(StockOverflowException):
            ing.replenish(11)

    def test_16_replenish_full_stock(self):
        """이미 가득 찬 재고에 보충 시도"""
        ing = _ing(100, max_cap=100)
        with self.assertRaises(StockOverflowException):
            ing.replenish(1)

    def test_17_controller_admin_replenish_overflow(self):
        """관리자 재고 보충 - 최대 용량 초과"""
        self.ctrl = _make_controller(stock=95)
        with self.assertRaises(StockOverflowException):
            self.ctrl.admin_replenish("bean", 10)

    # ══ InsufficientChangeException ═════════════════════════════

    def test_18_dispense_no_reserve(self):
        """잔돈 보유량 전무"""
        r = _reserve({})
        with self.assertRaises(InsufficientChangeException):
            r.dispense(1000)

    def test_19_dispense_wrong_denomination_only(self):
        """1000원 3개(3000원) 보유, 5000원 잔돈 반환 불가"""
        r = _reserve({1000: 3})
        with self.assertRaises(InsufficientChangeException):
            r.dispense(5000)

    def test_20_controller_cash_insufficient_change(self):
        """잔돈 부족으로 결제 실패 → 장바구니 유지"""
        self.ctrl = _make_controller(reserve=_reserve({}))
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {}, 1)  # 3000원
        self.ctrl.start_cash_payment()
        self.ctrl.insert_cash(5000)
        with self.assertRaises(InsufficientChangeException):
            self.ctrl.process_cash_payment()
        self.assertFalse(self.ctrl.cart.is_empty())  # 장바구니 유지 확인

    def test_21_cash_process_zero_reserve_exact(self):
        """투입=결제 금액이지만 잔돈 보유량 무관 → 잔돈 0원 정상"""
        r = _reserve({})  # 잔돈 없음
        p = CashPayment(3000, r)
        p.insert(1000)
        p.insert(1000)
        p.insert(1000)  # 정확히 3000원 투입
        result = p.process()
        self.assertEqual(result, {})  # 잔돈 0 → 예외 없음

    # ══ PaymentException ════════════════════════════════════════

    def test_22_card_insufficient_balance(self):
        """카드 잔액 부족 시뮬레이션"""
        with self.assertRaises(PaymentException):
            CardPayment(3000, fail_reason="insufficient").process()

    def test_23_card_network_error(self):
        """카드 결제 오류 시뮬레이션"""
        with self.assertRaises(PaymentException):
            CardPayment(3000, fail_reason="error").process()

    # ══ AdminAuthException ══════════════════════════════════════

    def test_24_admin_wrong_password(self):
        """관리자 비밀번호 불일치"""
        self.ctrl = _make_controller()
        with self.assertRaises(AdminAuthException):
            self.ctrl.authenticate_admin("wrong")

    def test_25_admin_empty_password(self):
        """빈 문자열 비밀번호"""
        self.ctrl = _make_controller()
        with self.assertRaises(AdminAuthException):
            self.ctrl.authenticate_admin("")

    # ══ InvalidRecipeException ══════════════════════════════════

    def test_26_recipe_json_is_list(self):
        """recipes.json이 list 형태일 때"""
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "recipes.json")
            with open(path, "w") as f:
                json.dump([1, 2, 3], f)
            with self.assertRaises(InvalidRecipeException):
                DataManager(tmp).load_recipes()
        finally:
            shutil.rmtree(tmp)

    def test_27_recipe_json_is_string(self):
        """recipes.json이 문자열일 때"""
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "recipes.json")
            with open(path, "w") as f:
                json.dump("invalid", f)
            with self.assertRaises(InvalidRecipeException):
                DataManager(tmp).load_recipes()
        finally:
            shutil.rmtree(tmp)

    # ══ KioskException 공통 부모 검증 ═══════════════════════════

    def test_28_all_custom_exceptions_inherit_kiosk_exception(self):
        """모든 커스텀 예외가 KioskException을 상속하는지 확인"""
        classes = [
            InsufficientStockException, StockOverflowException,
            InsufficientChangeException, PaymentException,
            AdminAuthException, InvalidRecipeException,
        ]
        for cls in classes:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(issubclass(cls, KioskException))

    def test_29_all_custom_exceptions_caught_by_parent(self):
        """부모 예외로 일괄 catch 가능한지 확인"""
        cases = [
            lambda: _ing(0).deduct(1),
            lambda: _ing(100, 100).replenish(1),
            lambda: _reserve({}).dispense(1000),
            lambda: CardPayment(3000, "error").process(),
        ]
        for fn in cases:
            try:
                fn()
            except KioskException:
                pass  # 모두 KioskException으로 잡혀야 함
            else:
                self.fail(f"{fn} 이 KioskException을 발생시키지 않음")


if __name__ == "__main__":
    unittest.main(verbosity=2)
