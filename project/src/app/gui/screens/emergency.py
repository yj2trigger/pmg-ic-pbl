from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class EmergencyScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(20)

        icon = QLabel("⚠")
        icon.setFont(QFont("Malgun Gothic", 72))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("color: #f38ba8;")

        self._symptom_label = QLabel()
        self._symptom_label.setFont(QFont("Malgun Gothic", 28, QFont.Weight.Bold))
        self._symptom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._symptom_label.setStyleSheet("color: #f38ba8;")

        msg = QLabel(
            "이 증상은 응급 상황일 수 있습니다.\n"
            "즉시 119에 신고하거나 가까운 응급실을 방문하세요."
        )
        msg.setFont(QFont("Malgun Gothic", 18))
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)

        hotline = QLabel("응급 전화:  119")
        hotline.setFont(QFont("Malgun Gothic", 36, QFont.Weight.Bold))
        hotline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hotline.setStyleSheet("color: #f38ba8;")

        btn_back = QPushButton("← 증상 선택으로 돌아가기")
        btn_back.setMinimumHeight(56)
        btn_back.setFont(QFont("Malgun Gothic", 17))
        btn_back.clicked.connect(lambda: self._window.go_to_symptom_select())

        layout.addStretch()
        layout.addWidget(icon)
        layout.addWidget(self._symptom_label)
        layout.addWidget(msg)
        layout.addSpacing(16)
        layout.addWidget(hotline)
        layout.addStretch()
        layout.addWidget(btn_back)

    def setup(self, symptom_name: str) -> None:
        self._symptom_label.setText(symptom_name)
