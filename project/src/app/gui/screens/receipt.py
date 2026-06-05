# ──────────────────────────────────────────────────────────────────────────────
# receipt.py — 결제 완료 후 영수증 화면
# [역할]  결제 결과를 요약 출력하고 새 주문으로 돌아가는 마지막 화면.
# [선택 섹션]
#   - setup() 으로 항목·금액·결제 수단·거스름돈 주입 → 스크롤 가능 영역에 렌더링
#   - 할인 적용 시 소계/할인/합계 3단 표시
#   - "확인" 버튼 → go_to_idle()
# [의존성]
#   import  : datetime, PyQt6
#   사용하는 곳 : main_window.py → 현금/카드 결제 완료 콜백에서 setup() 후 전환
# ──────────────────────────────────────────────────────────────────────────────
import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ReceiptScreen(QWidget):
    # main_window.py 가 생성 시 window 주입.
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        # 고정 골격(제목, 스크롤 영역, 확인 버튼) 구성. 내용은 setup() 에서 채움.
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
        # 결제 완료 직후 main_window.py 가 호출. 기존 위젯 전부 지우고 새로 채움.
        # change_result: None → 현금 아님(카드), {} → 거스름돈 없음, 값 있으면 잔돈 분해.
        # 경계: subtotal != final_amount 일 때만 할인 행 추가.
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
        # 영수증 한 행 추가 헬퍼. setup() 내부 전용. center > right 우선순위 없음(center 먼저 체크).
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
        # 구분선 행 삽입. setup() 내부 전용.
        sep = QLabel("─" * 28)
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._receipt_layout.addWidget(sep)
