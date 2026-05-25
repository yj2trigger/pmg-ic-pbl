from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SymptomSelectScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 20)
        layout.setSpacing(14)

        title = QLabel("어떤 증상이 있으신가요?")
        title.setFont(QFont("Malgun Gothic", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidget(self._grid_widget)
        scroll.setWidgetResizable(True)

        cart_bar = QHBoxLayout()
        self._cart_summary = QLabel("")
        self._cart_summary.setFont(QFont("Malgun Gothic", 15))
        btn_cart = QPushButton("장바구니  →")
        btn_cart.setMinimumHeight(48)
        btn_cart.clicked.connect(lambda: self._window.go_to_cart())
        btn_admin = QPushButton("관리자")
        btn_admin.setMinimumHeight(48)
        btn_admin.setFixedWidth(90)
        btn_admin.setStyleSheet("font-size: 13px;")
        btn_admin.clicked.connect(lambda: self._window.go_to_admin_auth())
        cart_bar.addWidget(self._cart_summary, 1)
        cart_bar.addWidget(btn_cart)
        cart_bar.addWidget(btn_admin)

        layout.addWidget(title)
        layout.addWidget(scroll, 1)
        layout.addLayout(cart_bar)

    def refresh(self) -> None:
        while self._grid_layout.count():
            child = self._grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        symptom_group = self._window.controller.get_all_symptoms()
        symptoms = symptom_group.symptoms

        btn_all = QPushButton("전체 의약품 보기")
        btn_all.setMinimumHeight(72)
        btn_all.setFont(QFont("Malgun Gothic", 16))
        btn_all.clicked.connect(lambda: self._window.go_to_medicine_list(None))
        self._grid_layout.addWidget(btn_all, 0, 0, 1, 2)

        for i, symptom in enumerate(symptoms):
            row = 1 + i // 2
            col = i % 2
            if symptom.is_emergency:
                label = f"⚠ {symptom.name}"
                style = (
                    "background-color: #f38ba8; color: #1e1e2e;"
                    "border-color: #f38ba8; font-weight: bold;"
                )
                handler = lambda _c, s=symptom: self._window.go_to_emergency(s.name)
            else:
                label = symptom.name
                style = ""
                handler = lambda _c, s=symptom: self._window.go_to_medicine_list(s.name)

            btn = QPushButton(label)
            btn.setMinimumHeight(72)
            btn.setFont(QFont("Malgun Gothic", 16))
            if style:
                btn.setStyleSheet(style)
            btn.clicked.connect(handler)
            self._grid_layout.addWidget(btn, row, col)

        cart = self._window.cart
        if cart.is_empty():
            self._cart_summary.setText("")
        else:
            count = sum(item.quantity for item in cart.items)
            subtotal = cart.get_subtotal()
            self._cart_summary.setText(f"장바구니: {count}개 / {subtotal:,}원")
