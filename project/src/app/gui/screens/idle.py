# ──────────────────────────────────────────────────────────────────────────────
# idle.py — 대기 화면. 터치 한 번으로 메인 메뉴로 진입한다.
#
# [역할]
#   키오스크 시작·세션 종료 후 보여지는 화면.
#   화면 전체가 터치 영역이므로 버튼 없이 mousePressEvent를 오버라이드.
#
# [설계 원칙]
#   - 개별 위젯이 아닌 QWidget 전체에 mousePressEvent를 걸어
#     어느 좌표를 눌러도 go_to_main_menu()가 호출되도록 함.
#   - UI 구성은 _setup_ui()로 분리해 __init__을 단순하게 유지.
#
# [의존성]
#   import: PyQt6.QtWidgets, PyQt6.QtCore, PyQt6.QtGui
#   이 파일을 사용하는 곳:
#     main_window.py → self._idle = IdleScreen(self)
# ──────────────────────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class IdleScreen(QWidget):
    # 대기 화면 위젯. window: KioskWindow 역참조(화면 전환용)
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        # 세 텍스트를 수직 중앙 정렬. addStretch로 위아래 공백을 균등 배분.
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("🍦 EIK 키오스크")
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
        # 화면 전체를 단일 터치 영역으로 만들기 위해 오버라이드.
        # 어느 좌표를 눌러도 메인 메뉴로 전환 — 별도 버튼 불필요.
        self._window.go_to_main_menu()
