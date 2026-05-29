from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CartScreen(QWidget):
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
        btn_back = QPushButton("← 계속 쇼핑")
        btn_clear = QPushButton("전체 삭제")
        btn_pay = QPushButton("결제하기  →")
        btn_pay.setMinimumHeight(60)
        btn_pay.setFont(QFont("Malgun Gothic", 17))
        btn_back.clicked.connect(lambda: self._window.go_to_main_menu())
        btn_clear.clicked.connect(self._clear_cart)
        btn_pay.clicked.connect(lambda: self._window.go_to_payment_method())
        btn_row.addWidget(btn_back)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        btn_row.addWidget(btn_pay)

        layout.addWidget(title)
        layout.addWidget(scroll, 1)
        layout.addWidget(self._total_label)
        layout.addLayout(btn_row)

    def refresh(self) -> None:
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

    def update_item_qty(self, index: int, qty: int) -> None:
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
        self._window.controller.remove_from_cart(index)
        self.refresh()

    def _clear_cart(self) -> None:
        ctrl = self._window.controller
        cart = self._window.cart
        if not cart.is_empty():
            cart.clear(ctrl.ingredients)
            ctrl._save_ingredients()
        self.refresh()


class _CartItemRow(QFrame):
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
