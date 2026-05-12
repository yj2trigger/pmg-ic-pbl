import unittest
import tempfile
import shutil

from app.kiosk_controller import KioskController
from app.product import Coffee, CustomOption, OptionGroup
from app.ingredient import Ingredient
from app.cart import Cart
from app.payment import ChangeReserve
from app.data_manager import DataManager
from app.exceptions import AdminAuthException, StockOverflowException, InsufficientChangeException


def _build_controller(ingredients=None, change_reserve=None,
                      admin_config=None, products=None,
                      option_groups=None, logger=None):
    tmp = tempfile.mkdtemp()
    dm = DataManager(tmp)

    if products is None:
        products = [Coffee("p1", "아메리카노", 3000)]
    if ingredients is None:
        ingredients = {"bean": Ingredient("bean", "원두", 50, 100)}
    if change_reserve is None:
        change_reserve = ChangeReserve({50000: 3, 10000: 5, 5000: 5, 1000: 10})
    if admin_config is None:
        admin_config = {"password": "1234"}
    if option_groups is None:
        option_groups = []

    ctrl = KioskController(
        products=products,
        ingredients=ingredients,
        option_groups=option_groups,
        cart=Cart(),
        change_reserve=change_reserve,
        admin_config=admin_config,
        data_manager=dm,
        logger=logger,
    )
    ctrl._tmp = tmp  # tearDown에서 삭제하기 위해 보관
    return ctrl


class TestKioskController(unittest.TestCase):

    def tearDown(self):
        if hasattr(self, "ctrl"):
            shutil.rmtree(self.ctrl._tmp, ignore_errors=True)

    # ── 장바구니 ───────────────────────────────────────────────
    def test_add_to_cart_success(self):
        self.ctrl = _build_controller()
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {}, 1)
        self.assertFalse(self.ctrl.cart.is_empty())

    def test_get_final_amount_no_discount(self):
        self.ctrl = _build_controller()
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {}, 2)
        self.assertEqual(self.ctrl.get_final_amount(), 6000)

    def test_add_to_cart_deducts_stock(self):
        ing = Ingredient("bean", "원두", 10, 100)
        opt = CustomOption("size_l", "Large", 0, {"bean": 2})
        self.ctrl = _build_controller(ingredients={"bean": ing})
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {"size": opt}, 1)
        self.assertEqual(ing.stock, 8)  # 10 - 2×1

    # ── 결제 ──────────────────────────────────────────────────
    def test_cash_payment_clears_cart(self):
        self.ctrl = _build_controller()
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {}, 1)
        self.ctrl.start_cash_payment()
        self.ctrl.insert_cash(5000)
        self.ctrl.process_cash_payment()
        self.assertTrue(self.ctrl.cart.is_empty())

    def test_cash_payment_stock_not_restored(self):
        ing = Ingredient("bean", "원두", 10, 100)
        opt = CustomOption("size_l", "Large", 0, {"bean": 2})
        self.ctrl = _build_controller(ingredients={"bean": ing})
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {"size": opt}, 1)  # stock: 10 → 8
        self.ctrl.start_cash_payment()
        self.ctrl.insert_cash(5000)
        self.ctrl.process_cash_payment()
        self.assertEqual(ing.stock, 8)  # 결제 후 복원 없이 유지

    def test_card_payment_clears_cart(self):
        self.ctrl = _build_controller()
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {}, 1)
        self.ctrl.start_card_payment()
        self.ctrl.process_card_payment()
        self.assertTrue(self.ctrl.cart.is_empty())

    def test_insufficient_change_cart_preserved(self):
        reserve = ChangeReserve({50000: 0, 10000: 0, 5000: 0, 1000: 0})
        self.ctrl = _build_controller(change_reserve=reserve)
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {}, 1)  # 3000원
        self.ctrl.start_cash_payment()
        self.ctrl.insert_cash(5000)
        with self.assertRaises(InsufficientChangeException):
            self.ctrl.process_cash_payment()
        self.assertFalse(self.ctrl.cart.is_empty())  # 장바구니 유지

    def test_cancel_payment_returns_inserted(self):
        self.ctrl = _build_controller()
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {}, 1)
        self.ctrl.start_cash_payment()
        self.ctrl.insert_cash(1000)
        self.ctrl.insert_cash(1000)
        inserted = self.ctrl.cancel_payment()
        self.assertEqual(inserted, 2000)

    # ── 관리자 ─────────────────────────────────────────────────
    def test_admin_auth_correct(self):
        self.ctrl = _build_controller()
        self.assertTrue(self.ctrl.authenticate_admin("1234"))

    def test_admin_auth_wrong(self):
        self.ctrl = _build_controller()
        with self.assertRaises(AdminAuthException):
            self.ctrl.authenticate_admin("wrong")

    def test_admin_replenish_success(self):
        ing = Ingredient("bean", "원두", 50, 100)
        self.ctrl = _build_controller(ingredients={"bean": ing})
        self.ctrl.admin_replenish("bean", 20)
        self.assertEqual(ing.stock, 70)

    def test_admin_replenish_overflow(self):
        ing = Ingredient("bean", "원두", 90, 100)
        self.ctrl = _build_controller(ingredients={"bean": ing})
        with self.assertRaises(StockOverflowException):
            self.ctrl.admin_replenish("bean", 20)

    def test_admin_toggle_product(self):
        p = Coffee("p1", "아메리카노", 3000, is_available=True)
        self.ctrl = _build_controller(products=[p])
        self.ctrl.admin_toggle_product("p1", False)
        self.assertEqual(self.ctrl.get_available_products(), [])

    def test_admin_change_password(self):
        self.ctrl = _build_controller()
        self.ctrl.admin_change_password("9999")
        self.assertTrue(self.ctrl.authenticate_admin("9999"))

    # ── logger ─────────────────────────────────────────────────
    def test_logger_called(self):
        logs = []
        self.ctrl = _build_controller(logger=logs.append)
        p = self.ctrl.products[0]
        self.ctrl.add_to_cart(p, {}, 1)
        self.ctrl.start_cash_payment()
        self.ctrl.insert_cash(5000)
        self.ctrl.process_cash_payment()
        self.assertTrue(any("완료" in m for m in logs))


if __name__ == "__main__":
    unittest.main(verbosity=2)
