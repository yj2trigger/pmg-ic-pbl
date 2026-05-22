"""
각 화면의 단위 테스트.

mock_window: KioskWindow를 MagicMock으로 대체하여 화면만 독립 검증.
controller: 실제 KioskController (비즈니스 로직 검증 포함).

실행:
    pytest tests/test_gui_screens.py -v
"""
import pytest
from unittest.mock import MagicMock

from app.cart import OrderItem
from app.product import CustomOption


# ────────────────────────── IdleScreen ───────────────────────────

class TestIdleScreen:
    def test_renders(self, qapp, mock_window):
        from app.gui.screens.idle import IdleScreen
        screen = IdleScreen(mock_window)
        assert screen is not None

    def test_click_calls_go_to_main_menu(self, qapp, mock_window):
        from app.gui.screens.idle import IdleScreen
        from PyQt6.QtCore import QPointF, Qt
        from PyQt6.QtGui import QMouseEvent

        screen = IdleScreen(mock_window)
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(100, 100), QPointF(100, 100),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        screen.mousePressEvent(event)
        mock_window.go_to_main_menu.assert_called_once()


# ────────────────────────── MainMenuScreen ───────────────────────

class TestMainMenuScreen:
    def test_renders_without_error(self, qapp, mock_window):
        from app.gui.screens.main_menu import MainMenuScreen
        screen = MainMenuScreen(mock_window)
        screen.refresh()

    def test_cart_frame_hidden_when_empty(self, qapp, mock_window):
        from app.gui.screens.main_menu import MainMenuScreen
        screen = MainMenuScreen(mock_window)
        screen.refresh()
        assert not mock_window.controller.cart.is_empty() or not screen._cart_frame.isVisible()

    def test_coffee_btn_disabled_when_unavailable(self, qapp, mock_window):
        from app.gui.screens.main_menu import MainMenuScreen
        mock_window.controller.products[0].is_available = False
        mock_window.controller.products[1].is_available = False
        screen = MainMenuScreen(mock_window)
        screen.refresh()
        assert not screen._btn_coffee.isEnabled()
        # 복원
        mock_window.controller.products[0].is_available = True
        mock_window.controller.products[1].is_available = True

    def test_gummy_btn_enabled_when_available(self, qapp, mock_window):
        from app.gui.screens.main_menu import MainMenuScreen
        screen = MainMenuScreen(mock_window)
        screen.refresh()
        assert screen._btn_gummy.isEnabled()


# ────────────────────────── ProductListScreen ────────────────────

class TestProductListScreen:
    def test_title_coffee(self, qapp, mock_window):
        from app.gui.screens.product_list import ProductListScreen
        screen = ProductListScreen(mock_window)
        screen.setup("coffee")
        assert screen._title.text() == "커피 선택"

    def test_title_gummy(self, qapp, mock_window):
        from app.gui.screens.product_list import ProductListScreen
        screen = ProductListScreen(mock_window)
        screen.setup("gummy")
        assert screen._title.text() == "구미 선택"

    def test_product_buttons_created(self, qapp, mock_window):
        from app.gui.screens.product_list import ProductListScreen
        screen = ProductListScreen(mock_window)
        screen.setup("coffee")
        # 커피 상품 2개(c1, c2) → 버튼 2개
        assert screen._grid.count() == 2


# ────────────────────────── CustomizeScreen ──────────────────────

class TestCustomizeScreen:
    def test_renders_with_coffee(self, qapp, mock_window, sample_products):
        from app.gui.screens.customize import CustomizeScreen
        screen = CustomizeScreen(mock_window)
        screen.setup(sample_products[0])
        assert "아메리카노" in screen._title.text()

    def test_option_groups_created(self, qapp, mock_window, sample_products):
        from app.gui.screens.customize import CustomizeScreen
        screen = CustomizeScreen(mock_window)
        screen.setup(sample_products[0])  # coffee: 4 groups (size, temperature, shot, sweetness)
        assert len(screen._option_widgets) == 4

    def test_error_on_no_option_selected(self, qapp, mock_window, sample_products):
        from app.gui.screens.customize import CustomizeScreen
        screen = CustomizeScreen(mock_window)
        screen.setup(sample_products[0])
        screen._confirm()
        assert screen._error_label.text() != ""
        mock_window.go_to_main_menu.assert_not_called()

    def test_adds_to_cart_when_all_options_selected(self, qapp, mock_window, sample_products):
        from app.gui.screens.customize import CustomizeScreen
        screen = CustomizeScreen(mock_window)
        screen.setup(sample_products[0])
        for w in screen._option_widgets:
            btns = w._btn_group.buttons()
            if btns:
                btns[0].setChecked(True)
        screen._confirm()
        assert not mock_window.controller.cart.is_empty()
        mock_window.go_to_main_menu.assert_called_once()
        # 정리
        mock_window.controller.cart.clear(mock_window.controller.ingredients)

    def test_price_label_updates_on_qty_change(self, qapp, mock_window, sample_products):
        from app.gui.screens.customize import CustomizeScreen
        screen = CustomizeScreen(mock_window)
        screen.setup(sample_products[0])
        for w in screen._option_widgets:
            btns = w._btn_group.buttons()
            if btns:
                btns[0].setChecked(True)
        screen._qty_spin.setValue(2)
        label = screen._price_label.text()
        assert "원" in label


# ────────────────────────── CartScreen ───────────────────────────

class TestCartScreen:
    def test_empty_cart_renders(self, qapp, mock_window):
        from app.gui.screens.cart import CartScreen
        screen = CartScreen(mock_window)
        screen.refresh()
        assert mock_window.controller.cart.is_empty()

    def test_item_added_shows_in_cart(self, qapp, mock_window, sample_products):
        from app.gui.screens.cart import CartScreen
        opt = CustomOption("size_s", "Small", 0, {"bean": 1})
        item = OrderItem(sample_products[0], {"size": opt}, 1)
        ctrl = mock_window.controller
        ctrl.cart.add_item(item, ctrl.ingredients)

        screen = CartScreen(mock_window)
        screen.refresh()
        # items_layout에 CartItemRow 위젯이 있어야 함
        assert screen._items_layout.count() >= 1
        ctrl.cart.clear(ctrl.ingredients)

    def test_total_label_shows_amount(self, qapp, mock_window, sample_products):
        from app.gui.screens.cart import CartScreen
        opt = CustomOption("size_s", "Small", 0, {"bean": 1})
        item = OrderItem(sample_products[0], {"size": opt}, 2)
        ctrl = mock_window.controller
        ctrl.cart.add_item(item, ctrl.ingredients)

        screen = CartScreen(mock_window)
        screen.refresh()
        assert "6,000" in screen._total_label.text()
        ctrl.cart.clear(ctrl.ingredients)

    def test_remove_item(self, qapp, mock_window, sample_products):
        from app.gui.screens.cart import CartScreen
        opt = CustomOption("size_s", "Small", 0, {"bean": 1})
        item = OrderItem(sample_products[0], {"size": opt}, 1)
        ctrl = mock_window.controller
        ctrl.cart.add_item(item, ctrl.ingredients)

        screen = CartScreen(mock_window)
        screen.remove_item(0)
        assert ctrl.cart.is_empty()

    def test_update_qty(self, qapp, mock_window, sample_products):
        from app.gui.screens.cart import CartScreen
        opt = CustomOption("size_s", "Small", 0, {"bean": 1})
        item = OrderItem(sample_products[0], {"size": opt}, 1)
        ctrl = mock_window.controller
        ctrl.cart.add_item(item, ctrl.ingredients)

        screen = CartScreen(mock_window)
        screen.update_item_qty(0, 3)
        assert ctrl.cart.items[0].quantity == 3
        ctrl.cart.clear(ctrl.ingredients)


# ────────────────────────── PaymentMethodScreen ──────────────────

class TestPaymentMethodScreen:
    def test_renders(self, qapp, mock_window):
        from app.gui.screens.payment_method import PaymentMethodScreen
        screen = PaymentMethodScreen(mock_window)
        screen.refresh()

    def test_amount_label_updated(self, qapp, mock_window, sample_products):
        from app.gui.screens.payment_method import PaymentMethodScreen
        opt = CustomOption("size_s", "Small", 0, {"bean": 1})
        item = OrderItem(sample_products[0], {"size": opt}, 1)
        ctrl = mock_window.controller
        ctrl.cart.add_item(item, ctrl.ingredients)

        screen = PaymentMethodScreen(mock_window)
        screen.refresh()
        assert "3,000" in screen._amount_label.text()
        ctrl.cart.clear(ctrl.ingredients)


# ────────────────────────── CashPaymentScreen ────────────────────

class TestCashPaymentScreen:
    def _add_coffee(self, mock_window, sample_products):
        opt = CustomOption("size_s", "Small", 0, {"bean": 1})
        item = OrderItem(sample_products[0], {"size": opt}, 1)
        ctrl = mock_window.controller
        ctrl.cart.add_item(item, ctrl.ingredients)

    def test_renders(self, qapp, mock_window, sample_products):
        from app.gui.screens.cash_payment import CashPaymentScreen
        self._add_coffee(mock_window, sample_products)
        ctrl = mock_window.controller
        ctrl.start_cash_payment()

        screen = CashPaymentScreen(mock_window)
        screen.refresh()
        mock_window.controller.cancel_payment()
        ctrl.cart.clear(ctrl.ingredients)

    def test_complete_btn_disabled_initially(self, qapp, mock_window, sample_products):
        from app.gui.screens.cash_payment import CashPaymentScreen
        self._add_coffee(mock_window, sample_products)
        ctrl = mock_window.controller
        ctrl.start_cash_payment()

        screen = CashPaymentScreen(mock_window)
        screen.refresh()
        assert not screen._btn_complete.isEnabled()
        ctrl.cancel_payment()
        ctrl.cart.clear(ctrl.ingredients)

    def test_insert_cash_updates_status(self, qapp, mock_window, sample_products):
        from app.gui.screens.cash_payment import CashPaymentScreen
        self._add_coffee(mock_window, sample_products)
        ctrl = mock_window.controller
        ctrl.start_cash_payment()

        screen = CashPaymentScreen(mock_window)
        screen.refresh()
        screen._insert_cash(1000)
        assert "1,000" in screen._status_label.text()
        ctrl.cancel_payment()
        ctrl.cart.clear(ctrl.ingredients)


# ────────────────────────── ReceiptScreen ────────────────────────

class TestReceiptScreen:
    def test_renders_with_cash(self, qapp, mock_window, sample_products):
        from app.gui.screens.receipt import ReceiptScreen
        opt = CustomOption("size_s", "Small", 0, {})
        item = OrderItem(sample_products[0], {"size": opt}, 2)
        screen = ReceiptScreen(mock_window)
        screen.setup([item], 6000, "현금", {1000: 2})
        assert screen is not None

    def test_renders_with_card(self, qapp, mock_window, sample_products):
        from app.gui.screens.receipt import ReceiptScreen
        opt = CustomOption("size_s", "Small", 0, {})
        item = OrderItem(sample_products[0], {"size": opt}, 1)
        screen = ReceiptScreen(mock_window)
        screen.setup([item], 3000, "카드")
        assert screen is not None


# ────────────────────────── AdminAuthScreen ──────────────────────

class TestAdminAuthScreen:
    def test_renders(self, qapp, mock_window):
        from app.gui.screens.admin_auth import AdminAuthScreen
        screen = AdminAuthScreen(mock_window)
        assert screen is not None

    def test_correct_password_navigates(self, qapp, mock_window):
        from app.gui.screens.admin_auth import AdminAuthScreen
        screen = AdminAuthScreen(mock_window)
        screen._pw_input.setText("1234")
        screen._authenticate()
        mock_window.go_to_admin_menu.assert_called_once()

    def test_wrong_password_shows_error(self, qapp, mock_window):
        from app.gui.screens.admin_auth import AdminAuthScreen
        screen = AdminAuthScreen(mock_window)
        screen._pw_input.setText("wrong")
        screen._authenticate()
        assert screen._error_label.text() != ""
        mock_window.go_to_admin_menu.assert_not_called()

    def test_reset_clears_fields(self, qapp, mock_window):
        from app.gui.screens.admin_auth import AdminAuthScreen
        screen = AdminAuthScreen(mock_window)
        screen._pw_input.setText("test")
        screen._error_label.setText("에러")
        screen.reset()
        assert screen._pw_input.text() == ""
        assert screen._error_label.text() == ""


# ────────────────────────── AdminMenuScreen ──────────────────────

class TestAdminMenuScreen:
    def test_renders(self, qapp, mock_window):
        from app.gui.screens.admin_menu import AdminMenuScreen
        screen = AdminMenuScreen(mock_window)
        screen.refresh()
        assert screen._status_label.text() == ""

    def test_show_cash_no_crash(self, qapp, mock_window):
        from app.gui.screens.admin_menu import AdminMenuScreen
        from unittest.mock import patch
        screen = AdminMenuScreen(mock_window)
        with patch("app.gui.screens.admin_menu.QMessageBox.information"):
            screen._show_cash()

    def test_add_cash_updates_reserve(self, qapp, mock_window):
        from app.gui.screens.admin_menu import _AddCashDialog
        ctrl = mock_window.controller
        before = ctrl.change_reserve.reserve.get(10000, 0)
        dlg = _AddCashDialog()
        dlg._denom_combo.setCurrentIndex(
            [dlg._denom_combo.itemData(i) for i in range(dlg._denom_combo.count())].index(10000)
        )
        dlg._count_spin.setValue(5)
        dlg._accept_data()
        denomination, count = dlg.result_data
        ctrl.admin_add_cash(denomination, count)
        assert ctrl.change_reserve.reserve[10000] == before + 5
