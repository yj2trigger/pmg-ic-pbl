from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QApplication

if TYPE_CHECKING:
    from app.drug_controller import DrugController
    from app.cart import Cart
    from app.payment import ChangeReserve


def run_gui(
    controller: "DrugController",
    cart: "Cart",
    change_reserve: "ChangeReserve",
) -> int:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    from app.gui.main_window import KioskWindow

    window = KioskWindow(controller, cart, change_reserve)
    window.showMaximized()
    return app.exec()
