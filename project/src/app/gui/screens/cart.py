# ──────────────────────────────────────────────────────────────────────────────
# cart.py — 장바구니 화면 (수량 조절·삭제·전체 삭제·결제 진입)
# [역할]  cart.items를 행 단위로 렌더링하고 수량 변경/삭제를 컨트롤러에 위임한다
# [선택 섹션]  _CartItemRow 내부 클래스가 행 단위 위젯을 담당
#             lambda가 생성 시점의 qty를 캡처하므로 refresh() 없이 누적 클릭 시 qty 불일치 가능
# [의존성]
#   직접 접근 : window.cart (cart.items, cart.is_empty, cart.get_subtotal, cart.clear)
#              ctrl._save_ingredients() — private, 리팩터링 대상
#   컨트롤러  : ctrl.remove_from_cart(), ctrl.update_cart_qty()
#   호출처   : main_window.py → self._cart = CartScreen(self)
# ──────────────────────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CartScreen(QWidget):
    # 장바구니 화면 위젯. 항목 변경마다 refresh()로 전체 재렌더링한다
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(14)

        title = QLabel("장바구니")
        title.setFont(QFont("Malgun Gothic", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._items_area = QWidget()
        self._items_layout = QVBoxLayout(self._items_area)
        self._items_layout.setSpacing(8)
        scroll = QScrollArea()
        scroll.setWidget(self._items_area)
        scroll.setWidgetResizable(True)

        self._total_label = QLabel()
        self._total_label.setFont(QFont("Malgun Gothic", 20, QFont.Weight.Bold))
        self._total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._total_label.setStyleSheet("color: #a6e3a1;")

        btn_row = QHBoxLayout()
        btn_back = QPushButton("← 계속 쇼핑")
        btn_clear = QPushButton("전체 삭제")
        self._btn_pay = QPushButton("결제하기  →")
        self._btn_pay.setMinimumHeight(60)
        self._btn_pay.setFont(QFont("Malgun Gothic", 17))
        btn_back.clicked.connect(lambda: self._window.go_to_main_menu())
        btn_clear.clicked.connect(self._clear_cart)
        self._btn_pay.clicked.connect(lambda: self._window.go_to_payment_method())
        btn_row.addWidget(btn_back)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_pay)

        layout.addWidget(title)
        layout.addWidget(scroll, 1)
        layout.addWidget(self._total_label)
        layout.addLayout(btn_row)

    def refresh(self) -> None:
        # WHY: PyQt 위젯을 직접 교체하는 방식이므로 기존 행을 deleteLater()로 정리해야
        #      메모리 누수 없이 재렌더링할 수 있다
        # 호출처: update_item_qty(), remove_item(), _clear_cart(), 외부에서 항목 변경 후
        cart = self._window.cart

        while self._items_layout.count():
            child = self._items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if cart.is_empty():
            lbl = QLabel("장바구니가 비어 있습니다.")
            lbl.setFont(QFont("Malgun Gothic", 16))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._items_layout.addWidget(lbl)
            self._total_label.setText("")
        else:
            for i, item in enumerate(cart.items):
                row = _CartItemRow(i, item, self)
                self._items_layout.addWidget(row)
            self._items_layout.addStretch()
            self._total_label.setText(f"합계: {cart.get_subtotal():,}원")
        self._btn_pay.setEnabled(not self._window.cart.is_empty())

    def update_item_qty(self, index: int, qty: int) -> None:
        # WHY: qty=0은 수량 0이 아닌 "항목 제거" 의미 — remove_from_cart로 분기해야 한다
        #      컨트롤러 예외를 여기서 잡아 사용자에게 표시한 뒤 항상 refresh()
        # 호출처: _CartItemRow의 − / + 버튼 lambda
        ctrl = self._window.controller
        try:
            if qty == 0:
                ctrl.remove_from_cart(index)
            else:
                ctrl.update_cart_qty(index, qty)
        except Exception as e:
            QMessageBox.warning(self, "오류", str(e))
        self.refresh()

    def remove_item(self, index: int) -> None:
        # 삭제 버튼 직접 클릭 경로 — update_item_qty(qty=0) 우회용
        # 호출처: _CartItemRow의 삭제 버튼 lambda
        self._window.controller.remove_from_cart(index)
        self.refresh()

    def _clear_cart(self) -> None:
        # WHY: cart.clear()는 재료 재고를 되돌리므로 ingredients를 넘겨야 한다
        #      _save_ingredients()는 private 직접 접근 — 추후 공개 메서드 이전 예정
        ctrl = self._window.controller
        cart = self._window.cart
        if not cart.is_empty():
            cart.clear(ctrl.ingredients)
            ctrl._save_ingredients()
        self.refresh()


class _CartItemRow(QFrame):
    # 장바구니 한 행 위젯. index·item·cart_screen을 받아 − / + / 삭제 버튼을 연결한다
    def __init__(self, index: int, item, cart_screen: CartScreen) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        name_lbl = QLabel(item.get_summary())
        name_lbl.setFont(QFont("Malgun Gothic", 14))

        price_lbl = QLabel(f"{item.calculate_subtotal():,}원")
        price_lbl.setFont(QFont("Malgun Gothic", 14))

        qty_lbl = QLabel(str(item.quantity))
        qty_lbl.setFont(QFont("Malgun Gothic", 15, QFont.Weight.Bold))
        qty_lbl.setMinimumWidth(30)
        qty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_minus = QPushButton("−")
        btn_plus = QPushButton("+")
        btn_remove = QPushButton("삭제")
        for btn in (btn_minus, btn_plus):
            btn.setFixedSize(44, 44)
            btn.setStyleSheet("padding: 0px; font-size: 20px; font-weight: bold;")
        btn_remove.setFixedHeight(44)

        # WHY: qty를 생성 시점에 고정 캡처 — 클릭마다 refresh()가 행을 재생성하므로
        #      누적 클릭이 발생하지 않는 정상 경로에서는 문제없다
        #      단, refresh() 없이 연속 클릭 시 qty 값이 stale해질 수 있다
        qty = item.quantity
        btn_minus.clicked.connect(
            lambda: cart_screen.update_item_qty(index, max(0, qty - 1))
        )
        btn_plus.clicked.connect(
            lambda: cart_screen.update_item_qty(index, qty + 1)
        )
        btn_remove.clicked.connect(lambda: cart_screen.remove_item(index))

        layout.addWidget(name_lbl, 1)
        layout.addWidget(price_lbl)
        layout.addWidget(btn_minus)
        layout.addWidget(qty_lbl)
        layout.addWidget(btn_plus)
        layout.addWidget(btn_remove)
