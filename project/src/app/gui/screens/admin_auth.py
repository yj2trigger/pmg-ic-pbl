from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AdminAuthScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(100, 80, 100, 80)
        layout.setSpacing(16)

        title = QLabel("관리자 인증")
        title.setFont(QFont("Malgun Gothic", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._pw_input = QLineEdit()
        self._pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw_input.setPlaceholderText("비밀번호를 입력하세요")
        self._pw_input.setMinimumHeight(52)
        self._pw_input.setFont(QFont("Malgun Gothic", 18))
        self._pw_input.returnPressed.connect(self._authenticate)

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: #f38ba8;")
        self._error_label.setFont(QFont("Malgun Gothic", 14))
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("취소")
        btn_confirm = QPushButton("확인")
        btn_cancel.setMinimumHeight(55)
        btn_confirm.setMinimumHeight(55)
        btn_cancel.clicked.connect(lambda: self._window.go_to_main_menu())
        btn_confirm.clicked.connect(self._authenticate)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_confirm)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(24)
        layout.addWidget(self._pw_input)
        layout.addWidget(self._error_label)
        layout.addSpacing(12)
        layout.addLayout(btn_row)
        layout.addStretch()

    def reset(self) -> None:
        self._pw_input.clear()
        self._error_label.setText("")
        self._pw_input.setFocus()

    def _authenticate(self) -> None:
        from app.password_utils import verify_password
        pw = self._pw_input.text().strip()
        config = self._window.controller.data_manager.load_admin_config() or {}
        if verify_password(pw, config.get("password", "")):
            self._window.go_to_admin_menu()
        else:
            self._error_label.setText("비밀번호가 올바르지 않습니다.")
            self._pw_input.clear()
