import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ReceiptScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 30, 80, 30)
        layout.setSpacing(12)

        title = QLabel("영  수  증")
        title.setFont(QFont("Malgun Gothic", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._receipt_area = QWidget()
        self._receipt_layout = QVBoxLayout(self._receipt_area)
        self._receipt_layout.setSpacing(4)
        scroll = QScrollArea()
        scroll.setWidget(self._receipt_area)
        scroll.setWidgetResizable(True)

        btn_confirm = QPushButton("확인  (처음으로 돌아갑니다)")
        btn_confirm.setMinimumHeight(60)
        btn_confirm.setFont(QFont("Malgun Gothic", 17))
        btn_confirm.setStyleSheet("color: #a6e3a1; border-color: #a6e3a1;")
        btn_confirm.clicked.connect(lambda: self._window.go_to_idle())

        layout.addWidget(title)
        layout.addWidget(scroll, 1)
        layout.addWidget(btn_confirm)

    def setup(
        self,
        items: list,
        final_amount: int,
        payment_method: str,
        change_result: dict | None = None,
    ) -> None:
        while self._receipt_layout.count():
            child = self._receipt_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._add("일시: " + now)
        self._sep()

        subtotal = 0
        for item in items:
            self._add(item.get_summary())
            self._add(f"    {item.calculate_subtotal():,}원", right=True)
            subtotal += item.calculate_subtotal()

        self._sep()
        if subtotal != final_amount:
            self._add(f"소계:   {subtotal:,}원")
            self._add(f"할인:  −{subtotal - final_amount:,}원")
        self._add(f"합계:   {final_amount:,}원", bold=True)
        self._add(f"결제 수단:  {payment_method}")

        if change_result is not None:
            if change_result:
                self._add("잔돈:")
                for denom, cnt in sorted(change_result.items(), reverse=True):
                    self._add(f"  {denom:,}원 × {cnt}장")
            else:
                self._add("잔돈: 없음")

        self._sep()
        self._add("감사합니다!  또 이용해 주세요.", bold=True, center=True)
        self._receipt_layout.addStretch()

    def _add(
        self,
        text: str,
        bold: bool = False,
        right: bool = False,
        center: bool = False,
    ) -> None:
        lbl = QLabel(text)
        f = QFont("Malgun Gothic", 14)
        f.setBold(bold)
        lbl.setFont(f)
        if center:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif right:
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._receipt_layout.addWidget(lbl)

    def _sep(self) -> None:
        sep = QLabel("─" * 28)
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._receipt_layout.addWidget(sep)
