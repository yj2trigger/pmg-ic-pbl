# ──────────────────────────────────────────────────────────────────────────────
# app.py — GUI 진입점. --gui 플래그가 있을 때만 PyQt6를 로드한다.
#
# [역할]
#   run_gui()를 export해 main.py가 도메인 객체를 조립한 뒤 호출하는 단일 진입점.
#   QApplication 생성·이벤트루프 실행·종료 코드 반환을 모두 담당한다.
#
# [설계 원칙]
#   - PyQt6 import를 이 파일 안에만 가둬, --gui 없는 경로에서 Qt 의존성을 피함.
#   - QApplication.instance() 선체크: pytest-qt 환경에서 앱이 이미 있으면 재사용.
#   - showMaximized() 대신 availableGeometry + FramelessWindowHint 조합:
#     프레임리스 창은 showMaximized()가 작업표시줄을 가리므로 직접 좌표를 지정.
#   - TYPE_CHECKING 가드: 런타임에 순환 import 없이 타입 힌트만 활성화.
#
# [의존성]
#   import: PyQt6.QtCore, PyQt6.QtWidgets, app.gui.main_window(지연)
#   이 파일을 사용하는 곳:
#     main.py → `from app.gui.app import run_gui` 후 run_gui(controller, cart, change_reserve)
# ──────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# 런타임엔 import되지 않음 — 타입 체커 전용. 순환 import 방지.
if TYPE_CHECKING:
    from app.kiosk_controller import KioskController
    from app.cart import Cart
    from app.payment import ChangeReserve


def run_gui(
    controller: "KioskController",
    cart: "Cart",
    change_reserve: "ChangeReserve",
) -> int:
    # pytest-qt 등이 이미 QApplication을 만들었으면 그것을 재사용
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # KioskWindow import를 여기서 해야 PyQt6가 없는 환경에서도 모듈 로드 가능
    from app.gui.main_window import KioskWindow

    window = KioskWindow(controller, cart, change_reserve)
    # 프레임리스: 타이틀바 없이 가용 영역(작업표시줄 제외)에 정확히 맞춤
    window.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    # availableGeometry = 화면 전체 - 작업표시줄. showMaximized()는 프레임리스 시 덮어씌움.
    window.setGeometry(QApplication.primaryScreen().availableGeometry())
    window.show()
    return app.exec()
