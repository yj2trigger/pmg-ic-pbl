from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton,
    QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MedicineListScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 20)
        layout.setSpacing(14)

        self._title = QLabel()
        self._title.setFont(QFont("Malgun Gothic", 24, QFont.Weight.Bold))
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidget(self._grid_widget)
        scroll.setWidgetResizable(True)

        btn_back = QPushButton("← 증상 선택으로")
        btn_back.setMinimumHeight(48)
        btn_back.clicked.connect(lambda: self._window.go_to_symptom_select())

        layout.addWidget(self._title)
        layout.addWidget(scroll, 1)
        layout.addWidget(btn_back)

    def setup(self, symptom_name: str | None) -> None:
        if symptom_name is None:
            self._title.setText("전체 의약품")
            medicines = self._window.controller.get_available_medicines()
        else:
            self._title.setText(f"{symptom_name} 관련 의약품")
            medicines = self._window.controller.get_medicines_for_symptom(symptom_name)

        while self._grid_layout.count():
            child = self._grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not medicines:
            lbl = QLabel("해당 증상에 맞는 의약품이 없습니다.")
            lbl.setFont(QFont("Malgun Gothic", 16))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._grid_layout.addWidget(lbl, 0, 0, 1, 2)
            return

        for i, medicine in enumerate(medicines):
            row, col = i // 2, i % 2
            card = _MedicineCard(medicine, self._window)
            self._grid_layout.addWidget(card, row, col)


class _MedicineCard(QFrame):
    def __init__(self, medicine, window) -> None:
        super().__init__()
        self._medicine = medicine
        self._window = window
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        name_lbl = QLabel(medicine.name)
        name_lbl.setFont(QFont("Malgun Gothic", 16, QFont.Weight.Bold))
        name_lbl.setWordWrap(True)

        price_lbl = QLabel(f"{medicine.base_price:,}원")
        price_lbl.setFont(QFont("Malgun Gothic", 14))
        price_lbl.setStyleSheet("color: #a6e3a1;")

        avail_lbl = QLabel("판매 중" if medicine.is_available else "판매 중지")
        avail_lbl.setFont(QFont("Malgun Gothic", 12))
        avail_lbl.setStyleSheet(
            "color: #a6e3a1;" if medicine.is_available else "color: #f38ba8;"
        )

        layout.addWidget(name_lbl)
        layout.addWidget(price_lbl)
        layout.addWidget(avail_lbl)

    def mousePressEvent(self, event) -> None:
        self._window.go_to_medicine_detail(self._medicine)
