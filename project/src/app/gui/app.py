from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QApplication

if TYPE_CHECKING:
    from app.kiosk_controller import KioskController


def run_gui(controller: KioskController) -> int:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from app.gui.main_window import KioskWindow

    window = KioskWindow(controller)
    window.showMaximized()
    return app.exec()
