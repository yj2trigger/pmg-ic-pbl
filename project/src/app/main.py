# ──────────────────────────────────────────────────────────────────────────────
# main.py — 애플리케이션 진입점. 도메인 객체를 조립하고 GUI를 구동한다.
#
# [역할]
#   _build_app(): DataManager → 도메인 객체(상품/재료/옵션/잔돈/장바구니/컨트롤러) 조립.
#   main(): _build_app() 호출 후 --gui 플래그가 있으면 run_gui() 위임.
#
# [DATA_DIR 결정 로직]
#   PyInstaller exe 단독 배포 시: %AppData%\EDK\data\ (영구 저장)
#   개발/테스트 시: src/app/data/ (로컬 상대 경로)
#   첫 실행(exe): 번들된 초기 데이터를 AppData로 복사.
#
# [초기화 시 수행하는 일]
#   1. change_reserve.json 없으면 기본값 생성
#   2. admin_config.json 없으면 기본 비밀번호 "1234" → scrypt 해시로 저장
#   3. 레거시 평문 비밀번호가 있으면 scrypt로 자동 재해시
#
# [의존성]
#   import: DataManager, KioskController, Cart, ChangeReserve, hash_password
#   이 파일을 사용하는 곳: python -m app.main --gui 또는 PyInstaller 번들 exe
# ──────────────────────────────────────────────────────────────────────────────

import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data_manager import DataManager
from app.kiosk_controller import KioskController
from app.cart import Cart
from app.password_utils import hash_password
from app.payment import ChangeReserve

if getattr(sys, "frozen", False):
    # exe 단독 배포: 데이터는 %AppData%\EDK\data\ 에 영구 저장
    _appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    DATA_DIR = os.path.join(_appdata, "EDK", "data")

    # 첫 실행: exe에 번들된 초기 데이터를 AppData로 복사
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        _bundled = os.path.join(sys._MEIPASS, "data")  # type: ignore[attr-defined]
        if os.path.isdir(_bundled):
            for _f in os.listdir(_bundled):
                shutil.copy(os.path.join(_bundled, _f), DATA_DIR)
else:
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

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
