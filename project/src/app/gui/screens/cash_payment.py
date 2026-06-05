# ──────────────────────────────────────────────────────────────────────────────
# cash_payment.py — 현금 투입 화면 (지폐 단위별 버튼 → 투입 → 결제 완료/취소)
# [역할]  사용자가 지폐를 한 장씩 투입하고 금액이 충족되면 결제를 완료하는 화면
# [선택 섹션]  결제 취소 시 투입 금액 전액 반환; 잔돈 부족 시 InsufficientChangeException 처리
# [의존성]
#   import  : app.exceptions.InsufficientChangeException, app.payment.ChangeReserve
#   직접 접근 : _window._active_payment (CashPayment), _window.cart.items, _window.cart.get_subtotal()
#   호출     : _window.controller._save_after_payment() — private, 리팩터링 대상
#   호출처   : main_window.py → self._cash_payment = CashPaymentScreen(self)
# ──────────────────────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.exceptions import InsufficientChangeException
from app.payment import ChangeReserve


class CashPaymentScreen(QWidget):
    # 현금 결제 화면 위젯. window를 통해 active_payment·cart에 직접 접근한다
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._snapshot: list = []   # refresh() 시점의 cart.items 스냅샷 — 영수증에 사용
        self._final_amount: int = 0  # refresh() 시점의 결제 총액 — 이후 cart 변동 무시
        self._setup_ui()

    def _setup_ui(self) -> None:
        # WHY: 지폐 버튼 배치는 ChangeReserve.DENOMINATIONS에서 동적 생성 — 권종 추가 시 자동 반영
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 30, 60, 30)
        layout.setSpacing(16)

        title = QLabel("현금 투입")
        title.setFont(QFont("Malgun Gothic", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._status_label = QLabel()
        self._status_label.setFont(QFont("Malgun Gothic", 17))
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        # WHY: 결제 도중 cart가 바뀌어도 영수증·잔액 계산이 흔들리지 않도록
        #      화면 진입 시점의 items·subtotal을 스냅샷으로 고정한다
        # 호출처: main_window.go_to_cash_payment() → CashPayment 생성 직후
        self._snapshot = list(self._window.cart.items)
        self._final_amount = self._window.cart.get_subtotal()
        self._update_status()

    def _update_status(self) -> None:
        # WHY: _active_payment가 None일 수 있으므로 방어적으로 읽는다
        #      can_complete() 충족 시 버튼을 초록으로 강조 — 시각적 완료 신호
        # 호출처: refresh(), _insert_cash()
        pmt = self._window._active_payment
        inserted = pmt.inserted_amount if pmt else 0
        remaining = max(0, self._final_amount - inserted)
        self._status_label.setText(
            f"결제: {self._final_amount:,}원 │ 투입: {inserted:,}원 │ 잔액: {remaining:,}원"
        )
        can_pay = pmt.can_complete() if pmt else False
        self._btn_complete.setEnabled(can_pay)
        if can_pay:
            self._btn_complete.setStyleSheet("color: #a6e3a1; border-color: #a6e3a1;")

    def _insert_cash(self, denomination: int) -> None:
        # WHY: _active_payment가 None이면 투입 자체를 무시 — 화면 전환 경합 방어
        # 호출처: 권종 버튼 clicked 시그널
        pmt = self._window._active_payment
        if pmt:
            pmt.insert(denomination)
        self._update_status()

    def _complete(self) -> None:
        # WHY: pmt.process()가 잔돈 배분을 결정하므로 실패(InsufficientChangeException) 시
        #      payment를 None으로 초기화하고 payment_method 화면으로 되돌린다
        #      성공 시 cart·payment 초기화 → _save_after_payment(재고+잔돈 JSON) → 영수증
        # 경계: _save_after_payment는 private — 추후 공개 메서드로 이전 예정
        pmt = self._window._active_payment
        try:
            change_result = pmt.process()
            self._window.cart.items = []
            self._window._active_payment = None
            self._window.controller._save_after_payment()  # 재고 + 잔돈 JSON 저장
            self._window.go_to_receipt(
                self._snapshot, self._final_amount, "현금", change_result
            )
        except InsufficientChangeException:
            refund = pmt.inserted_amount
            self._window._active_payment = None
            QMessageBox.warning(
                self,
                "잔돈 부족",
                f"잔돈이 부족하여 결제를 완료할 수 없습니다.\n"
                f"투입 금액 {refund:,}원을 반환합니다.",
            )
            self._window.go_to_payment_method()

    def _cancel(self) -> None:
        # WHY: 취소 시에도 투입 금액이 0보다 크면 반환 안내 메시지를 보여준다
        #      _active_payment를 None으로 초기화한 뒤 이동 — 잔여 상태 방지
        pmt = self._window._active_payment
        refund = pmt.inserted_amount if pmt else 0
        self._window._active_payment = None
        if refund > 0:
            QMessageBox.information(self, "취소", f"{refund:,}원을 반환합니다.")
        self._window.go_to_payment_method()
