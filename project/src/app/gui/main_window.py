from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from app.gui.voice_service import VoiceService

STYLESHEET = """
* {
    font-family: 'Malgun Gothic', 'Yu Gothic UI', 'Arial', sans-serif;
}
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 15px;
    font-weight: bold;
    min-height: 44px;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
}
QPushButton:pressed {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QPushButton:disabled {
    background-color: #1e1e2e;
    color: #585b70;
    border-color: #313244;
}
QPushButton:checked {
    background-color: #89b4fa;
    color: #1e1e2e;
    border-color: #89b4fa;
}
QLabel {
    background-color: transparent;
    color: #cdd6f4;
}
QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 16px;
}
QLineEdit:focus {
    border-color: #89b4fa;
}
QFrame {
    border: 1px solid #313244;
    border-radius: 8px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QScrollBar:vertical {
    background: #1e1e2e;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 4px;
    min-height: 20px;
}
QDialog {
    background-color: #1e1e2e;
}
QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 14px;
    min-height: 36px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
}
QSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 14px;
    min-height: 36px;
}
QMessageBox { background-color: #1e1e2e; }
"""


class KioskWindow(QMainWindow):
    def __init__(self, controller, cart, change_reserve) -> None:
        super().__init__()
        self.controller = controller
        self.cart = cart
        self.change_reserve = change_reserve
        self._active_payment = None
        self._customize_announced = False
        self.voice = VoiceService()
        self.setWindowTitle("🍦 아이스크림 키오스크")
        self.setStyleSheet(STYLESHEET)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        from app.gui.screens.idle import IdleScreen
        from app.gui.screens.main_menu import MainMenuScreen
        from app.gui.screens.customize import CustomizeScreen
        from app.gui.screens.cart import CartScreen
        from app.gui.screens.payment_method import PaymentMethodScreen
        from app.gui.screens.cash_payment import CashPaymentScreen
        from app.gui.screens.receipt import ReceiptScreen
        from app.gui.screens.admin_auth import AdminAuthScreen
        from app.gui.screens.admin_menu import AdminMenuScreen

        self._idle = IdleScreen(self)
        self._main_menu = MainMenuScreen(self)
        self._customize = CustomizeScreen(self)
        self._cart = CartScreen(self)
        self._payment_method = PaymentMethodScreen(self)
        self._cash_payment = CashPaymentScreen(self)
        self._receipt = ReceiptScreen(self)
        self._admin_auth = AdminAuthScreen(self)
        self._admin_menu = AdminMenuScreen(self)

        for screen in (
            self._idle, self._main_menu, self._customize,
            self._cart, self._payment_method, self._cash_payment,
            self._receipt, self._admin_auth, self._admin_menu,
        ):
            self._stack.addWidget(screen)

        self.go_to_idle()

    def go_to_idle(self) -> None:
        if not self.cart.is_empty():
            self.cart.clear(self.controller.ingredients)  # 세션 포기: 재고 복원
            self.controller._save_ingredients()
        self._active_payment = None
        self._customize_announced = False
        self._stack.setCurrentWidget(self._idle)
        self.voice.speak("화면을 터치하면 시작합니다")

    def go_to_main_menu(self) -> None:
        self._main_menu.refresh()
        self._stack.setCurrentWidget(self._main_menu)

    def go_to_customize(self, product) -> None:
        self._customize.setup(product)
        self._stack.setCurrentWidget(self._customize)
        if not self._customize_announced:
            self._customize_announced = True
            self.voice.speak("옵션을 선택해 주세요")

    def go_to_cart(self) -> None:
        self._cart.refresh()
        self._stack.setCurrentWidget(self._cart)
        self.voice.speak("장바구니를 확인해 주세요")

    def go_to_payment_method(self) -> None:
        self._payment_method.refresh()
        self._stack.setCurrentWidget(self._payment_method)
        self.voice.speak("결제 수단을 선택해 주세요")

    def go_to_cash_payment(self) -> None:
        from app.payment import CashPayment
        self._active_payment = CashPayment(self.cart.get_subtotal(), self.change_reserve)
        self._cash_payment.refresh()
        self._stack.setCurrentWidget(self._cash_payment)
        self.voice.speak("현금을 투입해 주세요")

    def go_to_card_payment(self) -> None:
        from app.payment import CardPayment
        snapshot = list(self.cart.items)
        final_amount = self.cart.get_subtotal()
        pmt = CardPayment(final_amount)
        try:
            pmt.process()
            self.cart.items = []
            self.controller._save_after_payment()  # 재고 + 잔돈 JSON 저장
            self.go_to_receipt(snapshot, final_amount, "카드")
        except Exception as e:
            QMessageBox.warning(self, "카드 결제 실패", str(e))
            self.go_to_payment_method()

    def go_to_receipt(
        self,
        items: list,
        final_amount: int,
        payment_method: str,
        change_result: dict | None = None,
    ) -> None:
        self._receipt.setup(items, final_amount, payment_method, change_result)
        self._stack.setCurrentWidget(self._receipt)
        self.voice.speak("결제가 완료되었습니다. 감사합니다")

    def go_to_admin_auth(self) -> None:
        self._admin_auth.reset()
        self._stack.setCurrentWidget(self._admin_auth)

    def go_to_admin_menu(self) -> None:
        self._admin_menu.refresh()
        self._stack.setCurrentWidget(self._admin_menu)
