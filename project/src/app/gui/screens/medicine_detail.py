from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox,
    QScrollArea, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.cart import OrderItem


class MedicineDetailScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._medicine = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 30, 60, 30)
        layout.setSpacing(14)

        self._name_label = QLabel()
        self._name_label.setFont(QFont("Malgun Gothic", 28, QFont.Weight.Bold))
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._price_label = QLabel()
        self._price_label.setFont(QFont("Malgun Gothic", 20))
        self._price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._price_label.setStyleSheet("color: #a6e3a1;")

        detail_area = QWidget()
        detail_layout = QVBoxLayout(detail_area)
        detail_layout.setSpacing(10)

        self._desc_label = QLabel()
        self._desc_label.setFont(QFont("Malgun Gothic", 14))
        self._desc_label.setWordWrap(True)

        self._dosage_label = QLabel()
        self._dosage_label.setFont(QFont("Malgun Gothic", 14))
        self._dosage_label.setWordWrap(True)

        self._caution_label = QLabel()
        self._caution_label.setFont(QFont("Malgun Gothic", 14))
        self._caution_label.setWordWrap(True)
        self._caution_label.setStyleSheet("color: #fab387;")

        detail_layout.addWidget(self._desc_label)
        detail_layout.addWidget(self._dosage_label)
        detail_layout.addWidget(self._caution_label)
        detail_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(detail_area)
        scroll.setWidgetResizable(True)

        qty_row = QHBoxLayout()
        qty_lbl = QLabel("수량:")
        qty_lbl.setFont(QFont("Malgun Gothic", 16))
        self._qty_spin = QSpinBox()
        self._qty_spin.setMinimum(1)
        self._qty_spin.setMaximum(9)
        self._qty_spin.setValue(1)
        self._qty_spin.setMinimumHeight(44)
        self._qty_spin.setFont(QFont("Malgun Gothic", 16))
        btn_add = QPushButton("장바구니에 담기  +")
        btn_add.setMinimumHeight(56)
        btn_add.setFont(QFont("Malgun Gothic", 17))
        btn_add.setStyleSheet("color: #a6e3a1; border-color: #a6e3a1;")
        btn_add.clicked.connect(self._add_to_cart)
        qty_row.addWidget(qty_lbl)
        qty_row.addWidget(self._qty_spin)
        qty_row.addStretch()
        qty_row.addWidget(btn_add)

        btn_back = QPushButton("← 목록으로")
        btn_back.setMinimumHeight(48)
        btn_back.clicked.connect(
            lambda: self._window.go_to_medicine_list(self._window._current_symptom_name)
        )

        layout.addWidget(self._name_label)
        layout.addWidget(self._price_label)
        layout.addWidget(scroll, 1)
        layout.addLayout(qty_row)
        layout.addWidget(btn_back)

    def setup(self, medicine) -> None:
        self._medicine = medicine
        self._name_label.setText(medicine.name)
        self._price_label.setText(f"{medicine.base_price:,}원")
        self._desc_label.setText(
            f"설명: {medicine.description}" if medicine.description else ""
        )
        self._dosage_label.setText(
            f"복용법: {medicine.dosage}" if medicine.dosage else ""
        )
        self._caution_label.setText(
            f"주의사항: {medicine.caution}" if medicine.caution else ""
        )
        self._qty_spin.setValue(1)

    def _add_to_cart(self) -> None:
        if self._medicine is None:
            return
        qty = self._qty_spin.value()
        item = OrderItem(self._medicine, {}, qty)
        self._window.cart.add_item(item, {})
        QMessageBox.information(
            self,
            "담기 완료",
            f"{self._medicine.name} {qty}개를 장바구니에 담았습니다.",
        )
        self._window.go_to_symptom_select()
