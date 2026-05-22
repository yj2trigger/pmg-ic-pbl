from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ProductListScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._product_type = "coffee"
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(16)

        self._title = QLabel()
        self._title.setFont(QFont("Malgun Gothic", 26, QFont.Weight.Bold))
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._grid_container = QWidget()
        self._grid = QGridLayout(self._grid_container)
        self._grid.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidget(self._grid_container)
        scroll.setWidgetResizable(True)

        btn_back = QPushButton("←  뒤로")
        btn_back.setMinimumHeight(48)
        btn_back.clicked.connect(lambda: self._window.go_to_main_menu())

        layout.addWidget(self._title)
        layout.addWidget(scroll, 1)
        layout.addWidget(btn_back)

    def setup(self, product_type: str) -> None:
        self._product_type = product_type
        label = "커피" if product_type == "coffee" else "구미"
        self._title.setText(f"{label} 선택")

        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        products = [
            p for p in self._window.controller.get_available_products()
            if p.product_type == product_type
        ]

        for i, product in enumerate(products):
            btn = QPushButton(
                f"{product.get_display_name()}\n{product.base_price:,}원~"
            )
            btn.setMinimumHeight(100)
            btn.setFont(QFont("Malgun Gothic", 16))
            btn.clicked.connect(
                lambda _checked, p=product: self._window.go_to_customize(p)
            )
            self._grid.addWidget(btn, i // 2, i % 2)
