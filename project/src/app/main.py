import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data_manager import DataManager
from app.drug_controller import DrugController
from app.cart import Cart
from app.payment import ChangeReserve

if getattr(sys, "frozen", False):
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), "data")
else:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

DEFAULT_CHANGE_RESERVE = {"50000": 5, "10000": 10, "5000": 20, "1000": 50}
DEFAULT_ADMIN_CONFIG = {"password": "1234"}


def _build_app() -> tuple[DrugController, Cart, ChangeReserve]:
    dm = DataManager(DATA_DIR)

    change_raw = dm.load_change_reserve()
    if not change_raw:
        dm.save_change_reserve(DEFAULT_CHANGE_RESERVE)
        change_raw = DEFAULT_CHANGE_RESERVE

    admin_config = dm.load_admin_config()
    if not admin_config:
        dm.save_admin_config(DEFAULT_ADMIN_CONFIG)

    return DrugController(dm), Cart(), ChangeReserve({int(k): v for k, v in change_raw.items()})


def main() -> None:
    controller, cart, change_reserve = _build_app()

    if "--gui" in sys.argv or getattr(sys, "frozen", False):
        from app.gui.app import run_gui
        sys.exit(run_gui(controller))
    else:
        from app.cli_view import CLIView
        CLIView(controller, cart, change_reserve).run()


if __name__ == "__main__":
    main()
