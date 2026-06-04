from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class IdleScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("🍦 아이스크림 키오스크")
        title.setFont(QFont("Malgun Gothic", 38, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #89b4fa;")

        sub = QLabel("나만의 아이스크림을 만들어 보세요.")
        sub.setFont(QFont("Malgun Gothic", 18))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        touch = QLabel("화면을 터치하면 시작합니다.")
        touch.setFont(QFont("Malgun Gothic", 22))
        touch.setAlignment(Qt.AlignmentFlag.AlignCenter)
        touch.setStyleSheet("color: #a6e3a1;")

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(24)
        layout.addWidget(sub)
        layout.addSpacing(48)
        layout.addWidget(touch)
        layout.addStretch()

    def mousePressEvent(self, event) -> None:
        self._window.go_to_main_menu()
