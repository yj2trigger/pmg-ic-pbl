"""KioskWindow 생성 및 화면 전환 통합 테스트."""
import pytest


def test_kiosk_window_creates(qapp, controller, cart, change_reserve):
    from app.gui.main_window import KioskWindow
    win = KioskWindow(controller, cart, change_reserve)
    assert win is not None
    win.close()


def test_initial_screen_is_idle(qapp, controller, cart, change_reserve):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.idle import IdleScreen
    win = KioskWindow(controller, cart, change_reserve)
    assert isinstance(win._stack.currentWidget(), IdleScreen)
    win.close()


@pytest.mark.parametrize("method,screen_module,screen_class", [
    ("go_to_symptom_select", "app.gui.screens.symptom_select", "SymptomSelectScreen"),
    ("go_to_cart",           "app.gui.screens.cart",           "CartScreen"),
    ("go_to_payment_method", "app.gui.screens.payment_method", "PaymentMethodScreen"),
    ("go_to_admin_auth",     "app.gui.screens.admin_auth",     "AdminAuthScreen"),
    ("go_to_admin_menu",     "app.gui.screens.admin_menu",     "AdminMenuScreen"),
])
def test_navigation(qapp, controller, cart, change_reserve, method, screen_module, screen_class):
    import importlib
    from app.gui.main_window import KioskWindow
    win = KioskWindow(controller, cart, change_reserve)
    getattr(win, method)()
    mod = importlib.import_module(screen_module)
    cls = getattr(mod, screen_class)
    assert isinstance(win._stack.currentWidget(), cls)
    win.close()


def test_go_to_medicine_list(qapp, controller, cart, change_reserve):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.medicine_list import MedicineListScreen
    win = KioskWindow(controller, cart, change_reserve)
    win.go_to_medicine_list("두통")
    assert isinstance(win._stack.currentWidget(), MedicineListScreen)
    win.close()


def test_go_to_medicine_list_all(qapp, controller, cart, change_reserve):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.medicine_list import MedicineListScreen
    win = KioskWindow(controller, cart, change_reserve)
    win.go_to_medicine_list(None)
    assert isinstance(win._stack.currentWidget(), MedicineListScreen)
    win.close()


def test_go_to_emergency(qapp, controller, cart, change_reserve):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.emergency import EmergencyScreen
    win = KioskWindow(controller, cart, change_reserve)
    win.go_to_emergency("심한 흉통")
    assert isinstance(win._stack.currentWidget(), EmergencyScreen)
    win.close()


def test_go_to_medicine_detail(qapp, controller, cart, change_reserve, sample_medicines):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.medicine_detail import MedicineDetailScreen
    win = KioskWindow(controller, cart, change_reserve)
    win.go_to_medicine_detail(sample_medicines[0])
    assert isinstance(win._stack.currentWidget(), MedicineDetailScreen)
    win.close()


def test_go_to_receipt(qapp, controller, cart, change_reserve, sample_medicines):
    from app.gui.main_window import KioskWindow
    from app.gui.screens.receipt import ReceiptScreen
    from app.cart import OrderItem
    item = OrderItem(sample_medicines[0], {}, 1)
    win = KioskWindow(controller, cart, change_reserve)
    win.go_to_receipt([item], 3000, "카드")
    assert isinstance(win._stack.currentWidget(), ReceiptScreen)
    win.close()


def test_go_to_idle_clears_cart(qapp, controller, cart, change_reserve, sample_medicines):
    from app.gui.main_window import KioskWindow
    from app.cart import OrderItem
    win = KioskWindow(controller, cart, change_reserve)
    # 창 생성 후 아이템 추가 (init 시 go_to_idle이 빈 카트 건너뜀)
    item = OrderItem(sample_medicines[0], {}, 2)
    cart.add_item(item, {})
    assert not cart.is_empty()
    win.go_to_idle()
    assert cart.is_empty()
    win.close()


def test_current_symptom_name_set_on_medicine_list(qapp, controller, cart, change_reserve):
    from app.gui.main_window import KioskWindow
    win = KioskWindow(controller, cart, change_reserve)
    win.go_to_medicine_list("두통")
    assert win._current_symptom_name == "두통"
    win.close()
