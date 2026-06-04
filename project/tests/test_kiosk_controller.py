import pytest
from unittest.mock import MagicMock

from app.cart import Cart
from app.exceptions import AdminAuthException, InsufficientStockException
from app.ice_cream import IceCreamProduct
from app.kiosk_controller import KioskController
from app.payment import ChangeReserve


@pytest.fixture
def products():
    return [
        IceCreamProduct("p1", "스틱", 3000, True,  "stick"),
        IceCreamProduct("p2", "스쿱", 4000, True,  "scoop"),
        IceCreamProduct("p3", "품절", 2000, False, "stick"),
    ]


@pytest.fixture
def ctrl(products):
    dm = MagicMock()
    dm.load_admin_config.return_value = {"password": "plain"}
    cart = Cart()
    reserve = ChangeReserve({1000: 50, 5000: 20, 10000: 10, 50000: 5})
    return KioskController(
        products, {}, [], cart, reserve,
        {"password": "plain"}, dm
    )


# ── 상품 조회 ──────────────────────────────────────────────────────────────

class TestGetAvailableProducts:
    def test_excludes_unavailable(self, ctrl):
        available = ctrl.get_available_products()
        assert len(available) == 2
        assert all(p.is_available for p in available)

    def test_returns_correct_types(self, ctrl):
        types = {p.product_type for p in ctrl.get_available_products()}
        assert "stick" in types
        assert "scoop" in types


# ── 장바구니 ───────────────────────────────────────────────────────────────

class TestCartOperations:
    def test_add_to_cart(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 2)
        assert len(ctrl.cart.items) == 1
        assert ctrl.cart.items[0].quantity == 2

    def test_add_saves_ingredients(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 1)
        ctrl.data_manager.save_ingredients.assert_called()

    def test_remove_from_cart(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 1)
        ctrl.remove_from_cart(0)
        assert ctrl.cart.is_empty()

    def test_update_cart_qty(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 1)
        ctrl.update_cart_qty(0, 3)
        assert ctrl.cart.items[0].quantity == 3

    def test_get_cart_subtotal(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 2)  # 3000 * 2 = 6000
        assert ctrl.get_cart_subtotal() == 6000

    def test_get_final_amount_no_discount(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 1)
        assert ctrl.get_final_amount() == ctrl.get_cart_subtotal()


# ── 결제 ──────────────────────────────────────────────────────────────────

class TestPayment:
    def test_start_cash_payment_creates_payment(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 1)
        ctrl.start_cash_payment()
        assert ctrl._active_payment is not None

    def test_insert_cash_accumulates(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 1)
        ctrl.start_cash_payment()
        ctrl.insert_cash(1000)
        ctrl.insert_cash(1000)
        assert ctrl._active_payment.inserted_amount == 2000

    def test_can_complete_when_enough_cash(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 1)  # 3000원
        ctrl.start_cash_payment()
        ctrl.insert_cash(5000)
        assert ctrl.can_complete_payment() is True

    def test_cancel_payment_returns_inserted(self, ctrl, products):
        ctrl.add_to_cart(products[0], {}, 1)
        ctrl.start_cash_payment()
        ctrl.insert_cash(1000)
        refund = ctrl.cancel_payment()
        assert refund == 1000
        assert ctrl._active_payment is None


# ── 관리자 ────────────────────────────────────────────────────────────────

class TestAdminOperations:
    def test_authenticate_correct_password(self, ctrl):
        from app.password_utils import hash_password, verify_password
        hashed = hash_password("1234")
        ctrl.admin_config["password"] = hashed
        assert ctrl.authenticate_admin("1234") is True

    def test_authenticate_wrong_password(self, ctrl):
        from app.password_utils import hash_password
        ctrl.admin_config["password"] = hash_password("1234")
        with pytest.raises(AdminAuthException):
            ctrl.authenticate_admin("wrong")

    def test_set_price(self, ctrl, products):
        ctrl.admin_set_price("p1", 5000)
        assert products[0].base_price == 5000
        ctrl.data_manager.save_products.assert_called()

    def test_set_price_unknown_id_raises(self, ctrl):
        with pytest.raises(KeyError):
            ctrl.admin_set_price("nonexistent", 1000)

    def test_toggle_product(self, ctrl, products):
        ctrl.admin_toggle_product("p1", False)
        assert products[0].is_available is False
        ctrl.data_manager.save_products.assert_called()

    def test_toggle_product_unknown_id_raises(self, ctrl):
        with pytest.raises(KeyError):
            ctrl.admin_toggle_product("nonexistent", True)

    def test_change_password_updates_memory(self, ctrl):
        from app.password_utils import hash_password
        new_hash = hash_password("newpass")
        ctrl.admin_change_password(new_hash)
        assert ctrl.admin_config["password"] == new_hash
        ctrl.data_manager.save_admin_config.assert_called()

    def test_add_cash(self, ctrl):
        before = ctrl.change_reserve.reserve[1000]
        ctrl.admin_add_cash(1000, 10)
        assert ctrl.change_reserve.reserve[1000] == before + 10
        ctrl.data_manager.save_change_reserve.assert_called()
