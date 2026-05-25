from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PaymentMethodScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
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
        amount = self._window.cart.get_subtotal()
        self._amount_label.setText(f"결제 금액: {amount:,}원")
