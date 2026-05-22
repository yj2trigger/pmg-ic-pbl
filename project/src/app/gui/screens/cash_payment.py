from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.exceptions import InsufficientChangeException
from app.payment import ChangeReserve


class CashPaymentScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._snapshot: list = []
        self._final_amount: int = 0
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 30, 60, 30)
        layout.setSpacing(16)

        title = QLabel("현금 투입")
        title.setFont(QFont("Malgun Gothic", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status_label = QLabel()
        self._status_label.setFont(QFont("Malgun Gothic", 17))
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Denomination buttons
        denom_grid = QGridLayout()
        denom_grid.setSpacing(12)
        denoms = sorted(ChangeReserve.DENOMINATIONS, reverse=True)
        for i, d in enumerate(denoms):
            btn = QPushButton(f"{d:,}원")
            btn.setMinimumHeight(75)
            btn.setFont(QFont("Malgun Gothic", 18))
            btn.clicked.connect(lambda _checked, denom=d: self._insert_cash(denom))
            denom_grid.addWidget(btn, i // 2, i % 2)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("취소")
        self._btn_complete = QPushButton("결제 완료  →")
        self._btn_complete.setMinimumHeight(60)
        self._btn_complete.setFont(QFont("Malgun Gothic", 17))
        self._btn_complete.setEnabled(False)
        btn_cancel.setMinimumHeight(60)
        btn_cancel.clicked.connect(self._cancel)
        self._btn_complete.clicked.connect(self._complete)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_complete)

        layout.addWidget(title)
        layout.addWidget(self._status_label)
        layout.addLayout(denom_grid)
        layout.addLayout(btn_row)

    def refresh(self) -> None:
        ctrl = self._window.controller
        self._snapshot = list(ctrl.cart.items)
        self._final_amount = ctrl.get_final_amount()
        self._update_status()

    def _update_status(self) -> None:
        ctrl = self._window.controller
        pmt = ctrl._active_payment
        inserted = pmt.inserted_amount if pmt else 0
        remaining = max(0, self._final_amount - inserted)
        self._status_label.setText(
            f"결제: {self._final_amount:,}원  │  투입: {inserted:,}원  │  잔액: {remaining:,}원"
        )
        can_pay = ctrl.can_complete_payment() if pmt else False
        self._btn_complete.setEnabled(can_pay)
        if can_pay:
            self._btn_complete.setStyleSheet("color: #a6e3a1; border-color: #a6e3a1;")

    def _insert_cash(self, denomination: int) -> None:
        self._window.controller.insert_cash(denomination)
        self._update_status()

    def _complete(self) -> None:
        ctrl = self._window.controller
        try:
            change_result = ctrl.process_cash_payment()
            self._window.go_to_receipt(
                self._snapshot, self._final_amount, "현금", change_result
            )
        except InsufficientChangeException:
            refund = ctrl.cancel_payment()
            QMessageBox.warning(
                self, "잔돈 부족",
                f"잔돈이 부족하여 결제를 완료할 수 없습니다.\n"
                f"투입 금액 {refund:,}원을 반환합니다.",
            )
            self._window.go_to_payment_method()

    def _cancel(self) -> None:
        refund = self._window.controller.cancel_payment()
        if refund > 0:
            QMessageBox.information(self, "취소", f"{refund:,}원을 반환합니다.")
        self._window.go_to_payment_method()
