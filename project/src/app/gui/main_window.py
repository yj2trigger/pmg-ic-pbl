# ──────────────────────────────────────────────────────────────────────────────
# main_window.py — 전체 화면 전환을 QStackedWidget으로 관리하는 메인 창
#
# [역할]
#   KioskWindow가 모든 화면 인스턴스를 소유하고, go_to_*() 메서드로 전환한다.
#   세션 상태(_active_payment, _customize_announced)를 보유하며
#   결제 완료·세션 포기 시점에 도메인 저장을 트리거한다.
#
# [핵심 구조]
#   QStackedWidget(_stack) — 9개 화면을 겹쳐 놓고 인덱스 전환
#   _active_payment        — 결제 진행 중인 CashPayment/CardPayment. 미결제 시 None.
#   _customize_announced   — 세션당 TTS "옵션을 선택해 주세요" 1회 보장 플래그
#
# [버그 수정 이력 / 설계 원칙]
#   - 화면 import를 __init__ 내부에서 수행: 각 화면이 `_window`를 역참조하므로
#     모듈 최상단 import 시 순환 import 발생. 지연 import로 회피.
#   - DEPENDENCY NOTE: go_to_cash_payment()가 CashPayment를 직접 생성하고
#     go_to_card_payment()가 cart.items를 직접 참조 — 리팩터링 대상으로 표시됨.
#
# [의존성]
#   import: PyQt6, app.gui.voice_service, app.payment(지연), 각 screens(지연)
#   이 파일을 사용하는 곳:
#     app.py → KioskWindow(controller, cart, change_reserve)
# ──────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from app.gui.voice_service import VoiceService

# Catppuccin Mocha 팔레트 기반 전역 스타일시트.
# 모든 QWidget에 일괄 적용되므로 각 화면에서 기본 색을 재정의하지 않아도 됨.
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
    # 모든 화면과 세션 상태를 소유하는 최상위 창
    def __init__(self, controller, cart, change_reserve) -> None:
        super().__init__()
        self.controller = controller
        self.cart = cart
        self.change_reserve = change_reserve
        # 결제 진행 중인 객체. 미결제 상태에서는 None으로 초기화해 방어적으로 참조 가능.
        self._active_payment = None
        # 세션당 커스터마이즈 TTS를 1회만 재생하기 위한 플래그. go_to_idle()에서 초기화.
        self._customize_announced = False
        self.voice = VoiceService()
        self.setWindowTitle("🍦 EIK 키오스크")
        self.setStyleSheet(STYLESHEET)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # 각 화면이 __init__ 인자로 self(_window)를 받아 역참조하므로
        # 모듈 상단 import 시 순환 import가 발생함 → 여기서 지연 import
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
        # 세션 포기 경로(뒤로가기 등): 장바구니가 비어있지 않으면 재고를 복원하고 비움
        if not self.cart.is_empty():
            self.cart.clear(self.controller.ingredients)  # 세션 포기: 재고 복원
            self.controller._save_ingredients()
        self._active_payment = None
        self._customize_announced = False
        self._stack.setCurrentWidget(self._idle)
        self.voice.speak("화면을 터치하면 시작합니다")

    def go_to_main_menu(self) -> None:
        # refresh()로 재고 변동을 반영한 뒤 전환
        self._main_menu.refresh()
        self._stack.setCurrentWidget(self._main_menu)

    def go_to_customize(self, product) -> None:
        # product: 선택된 상품 도메인 객체. setup()에 전달해 옵션 UI를 구성.
        # _customize_announced: 세션 첫 진입에만 TTS 재생 — 반복 클릭 시 음성 중복 방지
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
        # DEPENDENCY NOTE: CashPayment를 여기서 직접 생성 — 리팩터링 대상
        # cart.get_subtotal(): 결제 금액 확정 시점. 이후 금액 변경 없음.
        from app.payment import CashPayment
        self._active_payment = CashPayment(self.cart.get_subtotal(), self.change_reserve)
        self._cash_payment.refresh()
        self._stack.setCurrentWidget(self._cash_payment)
        self.voice.speak("현금을 투입해 주세요")

    def go_to_card_payment(self) -> None:
        # DEPENDENCY NOTE: cart.items 직접 접근 — 리팩터링 대상
        # snapshot: process() 전에 미리 복사. 결제 성공 후 cart를 비워도 영수증에 사용.
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
            # 카드 단말 오류 등 예외 발생 시 결제수단 선택으로 복귀
            QMessageBox.warning(self, "카드 결제 실패", str(e))
            self.go_to_payment_method()

    def go_to_receipt(
        self,
        items: list,
        final_amount: int,
        payment_method: str,
        change_result: dict | None = None,
    ) -> None:
        # change_result: 현금 결제 시 거스름돈 내역 dict. 카드 결제면 None.
        self._receipt.setup(items, final_amount, payment_method, change_result)
        self._stack.setCurrentWidget(self._receipt)
        self.voice.speak("결제가 완료되었습니다. 감사합니다")

    def go_to_admin_auth(self) -> None:
        # reset(): 이전 입력값 초기화 후 인증 화면으로 전환
        self._admin_auth.reset()
        self._stack.setCurrentWidget(self._admin_auth)

    def go_to_admin_menu(self) -> None:
        self._admin_menu.refresh()
        self._stack.setCurrentWidget(self._admin_menu)
