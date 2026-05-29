import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data_manager import DataManager
from app.kiosk_controller import KioskController
from app.cart import Cart
from app.password_utils import hash_password
from app.payment import ChangeReserve

if getattr(sys, "frozen", False):
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), "data")
else:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

DEFAULT_CHANGE_RESERVE = {"50000": 5, "10000": 10, "5000": 20, "1000": 50}


def _build_app() -> tuple[KioskController, Cart, ChangeReserve]:
    dm = DataManager(DATA_DIR)

    change_raw = dm.load_change_reserve()
    if not change_raw:
        dm.save_change_reserve(DEFAULT_CHANGE_RESERVE)
        change_raw = DEFAULT_CHANGE_RESERVE

    admin_config = dm.load_admin_config()
    if not admin_config:
        dm.save_admin_config({"password": hash_password("1234")})
        admin_config = dm.load_admin_config()
    elif not admin_config.get("password", "").startswith("scrypt$"):
        admin_config["password"] = hash_password(admin_config["password"])
        dm.save_admin_config(admin_config)

    products = dm.load_products()
    ingredients = dm.load_ingredients()
    option_groups = dm.load_option_groups()
    change_reserve = ChangeReserve({int(k): v for k, v in change_raw.items()})
    cart = Cart()

    controller = KioskController(
        products, ingredients, option_groups,
        cart, change_reserve, admin_config, dm,
    )
    return controller, cart, change_reserve


def main() -> None:
    controller, cart, change_reserve = _build_app()

    if "--gui" in sys.argv or getattr(sys, "frozen", False):
        from app.gui.app import run_gui
        sys.exit(run_gui(controller, cart, change_reserve))
    else:
        print("GUI 모드로 실행하세요: python -m app.main --gui")


if __name__ == "__main__":
    main()
