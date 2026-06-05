# ──────────────────────────────────────────────────────────────────────────────
# payment_method.py — 결제 수단 선택 화면 (현금 / 카드)
# [역할]  장바구니 확인 후 결제 수단을 고르는 중간 단계 화면.
# [선택 섹션]
#   - 최종 결제 금액을 상단에 표시 (refresh() 시 cart.get_subtotal() 로 갱신)
#   - 현금 → go_to_cash_payment(), 카드 → go_to_card_payment()
# [의존성]
#   import  : PyQt6
#   사용하는 곳 : main_window.py → go_to_payment_method() 에서 refresh() 후 전환
# ──────────────────────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PaymentMethodScreen(QWidget):
    # main_window.py 가 생성 시 window 주입. cart 접근 경로: self._window.cart
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        # 정적 레이아웃 + 버튼 연결. 금액 표시 라벨은 refresh() 에서 텍스트 갱신.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(18)

        self._amount_label = QLabel()
        self._amount_label.setFont(QFont("Malgun Gothic", 26, QFont.Weight.Bold))
        self._amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._amount_label.setStyleSheet("color: #a6e3a1;")

        sub = QLabel("결제 수단을 선택하세요")
        sub.setFont(QFont("Malgun Gothic", 18))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_cash = QPushButton("\U0001f4b5 현금 결제")
        btn_card = QPushButton("\U0001f4b3 카드 결제")
        btn_cancel = QPushButton("← 취소")
        btn_cash.setMinimumHeight(80)
        btn_card.setMinimumHeight(80)
        btn_cancel.setMinimumHeight(48)
        btn_cash.setFont(QFont("Malgun Gothic", 20))
        btn_card.setFont(QFont("Malgun Gothic", 20))

        btn_cash.clicked.connect(lambda: self._window.go_to_cash_payment())
        btn_card.clicked.connect(lambda: self._window.go_to_card_payment())
        btn_cancel.clicked.connect(lambda: self._window.go_to_cart())

        layout.addStretch()
        layout.addWidget(self._amount_label)
        layout.addWidget(sub)
        layout.addSpacing(16)
        layout.addWidget(btn_cash)
        layout.addWidget(btn_card)
        layout.addSpacing(16)
        layout.addWidget(btn_cancel)
        layout.addStretch()

    def refresh(self) -> None:
        # 화면 진입 시 main_window.py 가 호출. controller 대신 cart 직접 접근
        # (의존성 분리 미완 — process.md §5.3 참고).
        amount = self._window.cart.get_subtotal()
        self._amount_label.setText(f"결제 금액: {amount:,}원")
