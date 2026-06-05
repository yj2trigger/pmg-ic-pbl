# ──────────────────────────────────────────────────────────────────────────────
# main_menu.py — 상품 선택 화면 (스틱 / 스쿱 버튼 + 장바구니 요약 바)
# [역할]  메인 메뉴 화면 위젯. 사용자가 첫 번째로 마주치는 주문 진입 화면.
# [선택 섹션]
#   - 장바구니 요약 바: 카트가 비어 있으면 숨김, 항목 있으면 합계까지 표시
#   - 상품 버튼: 재고 부족 상품은 비활성화
# [의존성]
#   import  : PyQt6, app.gui.screens (구현 없음, QWidget 상속)
#   사용하는 곳 : main_window.py → QStackedWidget 에 추가 후 show_screen() 으로 전환
# ──────────────────────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MainMenuScreen(QWidget):
    # main_window.py 에서 생성 시 window 참조 주입. controller 접근 경로: self._window.controller
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        # 고정 레이아웃 구성. 버튼 연결까지 완료. 동적 데이터는 refresh() 에서 처리.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(14)

        title = QLabel("🍦 주문 메뉴")
        title.setFont(QFont("Malgun Gothic", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._cart_frame = QFrame()
        self._cart_inner = QVBoxLayout(self._cart_frame)
        self._cart_inner.setContentsMargins(12, 8, 12, 8)
        self._cart_frame.hide()

        self._btn_stick = QPushButton("🍦  스틱 아이스크림")
        self._btn_scoop = QPushButton("🍨  스쿱 아이스크림")
        for btn in (self._btn_stick, self._btn_scoop):
            btn.setMinimumHeight(80)
            btn.setFont(QFont("Malgun Gothic", 20))

        row = QHBoxLayout()
        row.addWidget(self._btn_stick)
        row.addWidget(self._btn_scoop)

        btn_cart = QPushButton("🛒  장바구니 / 결제")
        btn_admin = QPushButton("🔑  관리자")
        btn_back = QPushButton("←  처음 화면")
        btn_cart.setMinimumHeight(58)
        btn_admin.setMinimumHeight(50)
        btn_back.setMinimumHeight(44)

        self._btn_stick.clicked.connect(self._go_stick)
        self._btn_scoop.clicked.connect(self._go_scoop)
        btn_cart.clicked.connect(lambda: self._window.go_to_cart())
        btn_admin.clicked.connect(lambda: self._window.go_to_admin_auth())
        btn_back.clicked.connect(lambda: self._window.go_to_idle())

        layout.addWidget(title)
        layout.addWidget(self._cart_frame)
        layout.addLayout(row)
        layout.addWidget(btn_cart)
        layout.addWidget(btn_admin)
        layout.addStretch()
        layout.addWidget(btn_back)

    def _go_product(self, product_type: str, name: str) -> None:
        # 재고 있는 상품이면 커스터마이즈 화면으로 이동, 없으면 품절 다이얼로그 표시.
        # 호출: _go_stick(), _go_scoop() → 버튼 clicked 시그널 경유.
        # 경계: get_available_products() 반환 빈 리스트면 반드시 품절 분기로 진입.
        ctrl = self._window.controller
        product = next((p for p in ctrl.get_available_products() if p.product_type == product_type), None)
        if product:
            self._window.go_to_customize(product)
        else:
            QMessageBox.information(self, "품절", f"{name}이(가) 현재 품절입니다.")

    def _go_stick(self) -> None:
        self._go_product("stick", "스틱 아이스크림")

    def _go_scoop(self) -> None:
        self._go_product("scoop", "스쿱 아이스크림")

    def refresh(self) -> None:
        # 화면 전환 직전 main_window.py 가 호출. 장바구니 요약 바를 전부 재생성하고
        # 재고 상태에 따라 스틱/스쿱 버튼 활성화 여부를 갱신한다.
        # 기존 위젯을 deleteLater() 로 지워야 PyQt6 메모리 누수를 방지할 수 있음.
        ctrl = self._window.controller

        while self._cart_inner.count():
            child = self._cart_inner.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if ctrl.cart.is_empty():
            self._cart_frame.hide()
        else:
            header = QLabel("[ 장바구니 현황 ]")
            header.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
            self._cart_inner.addWidget(header)
            for item in ctrl.cart.items:
                lbl = QLabel(f"  •  {item.get_summary()}   {item.calculate_subtotal():,}원")
                self._cart_inner.addWidget(lbl)
            total_lbl = QLabel(f"  합계: {ctrl.get_final_amount():,}원")
            total_lbl.setFont(QFont("Malgun Gothic", 14, QFont.Weight.Bold))
            total_lbl.setStyleSheet("color: #a6e3a1;")
            self._cart_inner.addWidget(total_lbl)
            self._cart_frame.show()

        products = ctrl.get_available_products()
        self._btn_stick.setEnabled(any(p.product_type == "stick" for p in products))
        self._btn_scoop.setEnabled(any(p.product_type == "scoop" for p in products))
