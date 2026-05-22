from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MainMenuScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(14)

        title = QLabel("주문 메뉴")
        title.setFont(QFont("Malgun Gothic", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Cart summary panel
        self._cart_frame = QFrame()
        self._cart_frame.setObjectName("cart_frame")
        self._cart_inner = QVBoxLayout(self._cart_frame)
        self._cart_inner.setContentsMargins(12, 8, 12, 8)
        self._cart_frame.hide()

        # Product buttons
        self._btn_coffee = QPushButton("☕  커피 주문")
        self._btn_gummy = QPushButton("🍬  구미 주문")
        for btn in (self._btn_coffee, self._btn_gummy):
            btn.setMinimumHeight(70)
            btn.setFont(QFont("Malgun Gothic", 18))

        row = QHBoxLayout()
        row.addWidget(self._btn_coffee)
        row.addWidget(self._btn_gummy)

        btn_cart = QPushButton("🛒  장바구니 / 결제")
        btn_admin = QPushButton("🔑  관리자")
        btn_back = QPushButton("←  처음 화면")
        btn_cart.setMinimumHeight(58)
        btn_admin.setMinimumHeight(50)
        btn_back.setMinimumHeight(44)

        self._btn_coffee.clicked.connect(
            lambda: self._window.go_to_product_list("coffee")
        )
        self._btn_gummy.clicked.connect(
            lambda: self._window.go_to_product_list("gummy")
        )
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

    def refresh(self) -> None:
        ctrl = self._window.controller

        # Rebuild cart summary
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

        # Button availability
        products = ctrl.get_available_products()
        self._btn_coffee.setEnabled(
            any(p.product_type == "coffee" for p in products)
        )
        self._btn_gummy.setEnabled(
            any(p.product_type == "gummy" for p in products)
        )
