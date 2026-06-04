from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

if TYPE_CHECKING:
    from app.kiosk_controller import KioskController
    from app.cart import Cart
    from app.payment import ChangeReserve


def run_gui(
    controller: "KioskController",
    cart: "Cart",
    change_reserve: "ChangeReserve",
) -> int:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from app.gui.main_window import KioskWindow

    window = KioskWindow(controller, cart, change_reserve)
    # 프레임리스: 타이틀바 없이 가용 영역(작업표시줄 제외)에 정확히 맞춤
    window.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    window.setGeometry(QApplication.primaryScreen().availableGeometry())
    window.show()
    return app.exec()
