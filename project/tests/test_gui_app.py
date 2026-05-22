"""
KioskWindow 생성 및 화면 전환 통합 테스트.

실행:
    pytest tests/test_gui_app.py -v
    QT_QPA_PLATFORM=offscreen pytest tests/test_gui_app.py -v
"""
import pytest


def test_kiosk_window_creates(qapp, controller):
    from app.gui.main_window import KioskWindow
    win = KioskWindow(controller)
    assert win is not None
    win.close()


def test_initial_screen_is_idle(qapp, controller):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.idle import IdleScreen

    win = KioskWindow(controller)
    assert isinstance(win._stack.currentWidget(), IdleScreen)
    win.close()


@pytest.mark.parametrize("method,screen_module,screen_class", [
    ("go_to_main_menu",        "app.gui.screens.main_menu",       "MainMenuScreen"),
    ("go_to_cart",             "app.gui.screens.cart",            "CartScreen"),
    ("go_to_payment_method",   "app.gui.screens.payment_method",  "PaymentMethodScreen"),
    ("go_to_admin_auth",       "app.gui.screens.admin_auth",      "AdminAuthScreen"),
    ("go_to_admin_menu",       "app.gui.screens.admin_menu",      "AdminMenuScreen"),
])
def test_navigation(qapp, controller, method, screen_module, screen_class):
    import importlib
    from app.gui.main_window import KioskWindow

    win = KioskWindow(controller)
    getattr(win, method)()
    mod = importlib.import_module(screen_module)
    cls = getattr(mod, screen_class)
    assert isinstance(win._stack.currentWidget(), cls)
    win.close()


def test_go_to_product_list_coffee(qapp, controller):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.product_list import ProductListScreen

    win = KioskWindow(controller)
    win.go_to_product_list("coffee")
    assert isinstance(win._stack.currentWidget(), ProductListScreen)
    win.close()


def test_go_to_product_list_gummy(qapp, controller):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.product_list import ProductListScreen

    win = KioskWindow(controller)
    win.go_to_product_list("gummy")
    assert isinstance(win._stack.currentWidget(), ProductListScreen)
    win.close()


def test_go_to_customize(qapp, controller, sample_products):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.customize import CustomizeScreen

    win = KioskWindow(controller)
    win.go_to_customize(sample_products[0])
    assert isinstance(win._stack.currentWidget(), CustomizeScreen)
    win.close()


def test_go_to_receipt(qapp, controller):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.receipt import ReceiptScreen
    from app.cart import OrderItem
    from app.product import CustomOption

    opt = CustomOption("size_s", "Small", 0, {"bean": 1})
    item = OrderItem(controller.products[0], {"size": opt}, 1)

    win = KioskWindow(controller)
    win.go_to_receipt([item], 3000, "카드")
    assert isinstance(win._stack.currentWidget(), ReceiptScreen)
    win.close()


def test_go_to_idle_clears_cart(qapp, controller, sample_ingredients):
    from app.gui.main_window import KioskWindow
    from app.cart import OrderItem
    from app.product import CustomOption

    opt = CustomOption("size_s", "Small", 0, {"bean": 1})
    item = OrderItem(controller.products[0], {"size": opt}, 1)
    controller.cart.add_item(item, sample_ingredients)
    assert not controller.cart.is_empty()

    win = KioskWindow(controller)
    win.go_to_idle()
    assert controller.cart.is_empty()
    win.close()
