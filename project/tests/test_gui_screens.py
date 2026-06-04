"""각 화면 단위 테스트.

mock_window: KioskWindow를 MagicMock으로 대체하여 화면만 독립 검증.
controller: 실제 KioskController (비즈니스 로직 검증 포함).
"""
from unittest.mock import MagicMock, patch

from app.cart import OrderItem


# ─── IdleScreen ──────────────────────────────────────────────────────────────

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


# ─── CartScreen ──────────────────────────────────────────────────────────────

class TestCartScreen:
    def test_empty_cart_renders(self, qapp, mock_window):
        from app.gui.screens.cart import CartScreen
        screen = CartScreen(mock_window)
        screen.refresh()
        assert mock_window.cart.is_empty()

    def test_item_added_shows_in_cart(self, qapp, mock_window, sample_products):
        from app.gui.screens.cart import CartScreen
        item = OrderItem(sample_products[0], {}, 1)
        mock_window.cart.add_item(item, {})
        screen = CartScreen(mock_window)
        screen.refresh()
        assert screen._items_layout.count() >= 1
        mock_window.cart.clear({})

    def test_total_label_shows_amount(self, qapp, mock_window, sample_products):
        from app.gui.screens.cart import CartScreen
        item = OrderItem(sample_products[0], {}, 2)
        mock_window.cart.add_item(item, {})
        screen = CartScreen(mock_window)
        screen.refresh()
        assert "6,000" in screen._total_label.text()
        mock_window.cart.clear({})

    def test_remove_item(self, qapp, mock_window, sample_products):
        from app.gui.screens.cart import CartScreen
        item = OrderItem(sample_products[0], {}, 1)
        mock_window.cart.add_item(item, {})
        screen = CartScreen(mock_window)
        screen.remove_item(0)
        assert mock_window.cart.is_empty()

    def test_update_qty(self, qapp, mock_window, sample_products):
        from app.gui.screens.cart import CartScreen
        item = OrderItem(sample_products[0], {}, 1)
        mock_window.cart.add_item(item, {})
        screen = CartScreen(mock_window)
        screen.update_item_qty(0, 3)
        assert mock_window.cart.items[0].quantity == 3
        mock_window.cart.clear({})


# ─── PaymentMethodScreen ─────────────────────────────────────────────────────

class TestPaymentMethodScreen:
    def test_renders(self, qapp, mock_window):
        from app.gui.screens.payment_method import PaymentMethodScreen
        screen = PaymentMethodScreen(mock_window)
        screen.refresh()

    def test_amount_label_updated(self, qapp, mock_window, sample_products):
        from app.gui.screens.payment_method import PaymentMethodScreen
        item = OrderItem(sample_products[0], {}, 1)
        mock_window.cart.add_item(item, {})
        screen = PaymentMethodScreen(mock_window)
        screen.refresh()
        assert "3,000" in screen._amount_label.text()
        mock_window.cart.clear({})


# ─── CashPaymentScreen ───────────────────────────────────────────────────────

class TestCashPaymentScreen:
    def _setup_payment(self, mock_window, sample_products):
        from app.payment import CashPayment
        item = OrderItem(sample_products[0], {}, 1)
        mock_window.cart.add_item(item, {})
        mock_window._active_payment = CashPayment(
            mock_window.cart.get_subtotal(), mock_window.change_reserve
        )

    def test_renders(self, qapp, mock_window, sample_products):
        from app.gui.screens.cash_payment import CashPaymentScreen
        self._setup_payment(mock_window, sample_products)
        screen = CashPaymentScreen(mock_window)
        screen.refresh()
        mock_window.cart.clear({})
        mock_window._active_payment = None

    def test_complete_btn_disabled_initially(self, qapp, mock_window, sample_products):
        from app.gui.screens.cash_payment import CashPaymentScreen
        self._setup_payment(mock_window, sample_products)
        screen = CashPaymentScreen(mock_window)
        screen.refresh()
        assert not screen._btn_complete.isEnabled()
        mock_window.cart.clear({})
        mock_window._active_payment = None

    def test_insert_cash_updates_status(self, qapp, mock_window, sample_products):
        from app.gui.screens.cash_payment import CashPaymentScreen
        self._setup_payment(mock_window, sample_products)
        screen = CashPaymentScreen(mock_window)
        screen.refresh()
        screen._insert_cash(1000)
        assert "1,000" in screen._status_label.text()
        mock_window.cart.clear({})
        mock_window._active_payment = None


# ─── ReceiptScreen ───────────────────────────────────────────────────────────

class TestReceiptScreen:
    def test_renders_with_cash(self, qapp, mock_window, sample_products):
        from app.gui.screens.receipt import ReceiptScreen
        item = OrderItem(sample_products[0], {}, 2)
        screen = ReceiptScreen(mock_window)
        screen.setup([item], 6000, "현금", {1000: 2})
        assert screen is not None

    def test_renders_with_card(self, qapp, mock_window, sample_products):
        from app.gui.screens.receipt import ReceiptScreen
        item = OrderItem(sample_products[0], {}, 1)
        screen = ReceiptScreen(mock_window)
        screen.setup([item], 3000, "카드")
        assert screen is not None


# ─── AdminAuthScreen ─────────────────────────────────────────────────────────

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


# ─── AdminMenuScreen ─────────────────────────────────────────────────────────

class TestAdminMenuScreen:
    def test_renders(self, qapp, mock_window):
        from app.gui.screens.admin_menu import AdminMenuScreen
        screen = AdminMenuScreen(mock_window)
        screen.refresh()
        assert screen._status_label.text() == ""

    def test_show_cash_no_crash(self, qapp, mock_window):
        from app.gui.screens.admin_menu import AdminMenuScreen
        screen = AdminMenuScreen(mock_window)
        with patch("app.gui.screens.admin_menu.QMessageBox.information"):
            screen._show_cash()

    def test_add_cash_updates_reserve(self, qapp, mock_window):
        from app.gui.screens.admin_menu import _AddCashDialog
        before = mock_window.change_reserve.reserve.get(10000, 0)
        dlg = _AddCashDialog()
        idx = [dlg._denom_combo.itemData(i) for i in range(dlg._denom_combo.count())].index(10000)
        dlg._denom_combo.setCurrentIndex(idx)
        dlg._count_spin.setValue(5)
        dlg._accept_data()
        denomination, count = dlg.result_data
        mock_window.change_reserve.add_cash(denomination, count)
        assert mock_window.change_reserve.reserve[10000] == before + 5