# ──────────────────────────────────────────────────────────────────────────────
# kiosk_controller.py — GUI와 도메인 사이의 파사드(Facade). 모든 비즈니스 로직 진입점.
#
# [역할]
#   GUI가 직접 도메인 객체를 조작하지 않도록 중간 계층 역할.
#   상품 조회, 장바구니 관리, 결제 처리, 관리자 기능, 저장 트리거를 단일 인터페이스로 노출.
#
# [설계 원칙]
#   - GUI는 KioskController만 바라본다 (단방향 의존).
#     Cart·Ingredient·Product를 직접 import하지 않고, 이 파일 메서드만 호출.
#   - 단, main_window.py 일부 경로(go_to_cash_payment, go_to_card_payment)가
#     Cart.items를 직접 참조 — 리팩터링 대상으로 표시됨.
#   - _save_after_payment(): 현금/카드 결제 완료 공통 경로 — 재료+잔돈 JSON 저장.
#   - _active_payment: 진행 중인 결제 객체. 미결제 시 None. GUI에서도 참조함.
#
# [의존성]
#   import: app.cart (OrderItem, Cart), app.payment (CashPayment, CardPayment),
#           app.exceptions (AdminAuthException)
#   이 파일을 사용하는 곳:
#     main.py → KioskController(...) 인스턴스 생성
#     app.py → run_gui(controller, ...) 로 GUI에 전달
#     gui/main_window.py → self.controller.* 호출
# ──────────────────────────────────────────────────────────────────────────────

from app.cart import OrderItem, Cart
from app.payment import CashPayment, CardPayment
from app.exceptions import AdminAuthException


class KioskController:
    def __init__(self, products: list, ingredients: dict, option_groups: list,
                 cart: Cart, change_reserve, admin_config: dict,
                 data_manager, logger=None):
        self.products = products           # list[Product]
        self.ingredients = ingredients     # {ingredient_id: Ingredient}
        self.option_groups = option_groups # list[OptionGroup]
        self.cart = cart
        self.change_reserve = change_reserve
        self.admin_config = admin_config
        self.data_manager = data_manager
        self.logger = logger
        self._active_payment = None

    # ── 상품 ──────────────────────────────────────────────────
    def get_available_products(self) -> list:
        return [p for p in self.products if p.is_available]

    def get_option_groups(self, product) -> list:
        return [g for g in self.option_groups
                if g.is_active_for(product.product_type)]

    def get_unavailable_options(self, product, selected_options: dict) -> set:
        unavailable = set()
        for group in self.get_option_groups(product):
            for option in group.get_options():
                test_opts = {**selected_options, group.group_id: option}
                temp = OrderItem(product, test_opts, 1)
                if not temp.can_fulfill(self.ingredients):
                    unavailable.add(option.option_id)
        return unavailable

    # ── 장바구니 ───────────────────────────────────────────────
    def add_to_cart(self, product, options: dict, qty: int) -> None:
        item = OrderItem(product, options, qty)
        self.cart.add_item(item, self.ingredients)
        self._save_ingredients()

    def remove_from_cart(self, index: int) -> None:
        self.cart.remove_item(index, self.ingredients)
        self._save_ingredients()

    def update_cart_qty(self, index: int, qty: int) -> None:
        self.cart.update_quantity(index, qty, self.ingredients)
        self._save_ingredients()

    def get_cart_subtotal(self) -> int:
        return self.cart.get_subtotal()

    def get_discount(self) -> int:
        return 0  # discount_policy 후순위 — 미구현

    def get_final_amount(self) -> int:
        return self.get_cart_subtotal() - self.get_discount()

    # ── 결제 ──────────────────────────────────────────────────
    def start_cash_payment(self) -> None:
        self._active_payment = CashPayment(
            self.get_final_amount(), self.change_reserve
        )

    def insert_cash(self, denomination: int) -> int:
        self._active_payment.insert(denomination)
        return self._active_payment.inserted_amount

    def can_complete_payment(self) -> bool:
        return self._active_payment.can_complete()

    def process_cash_payment(self) -> dict:
        result = self._active_payment.process()
        self._save_after_payment()
        self.cart.items = []  # 결제 확정 → 재고 복원 없이 비움
        self._active_payment = None
        self.log("현금 결제 완료")
        return result

    def start_card_payment(self, fail_reason: str | None = None) -> None:
        self._active_payment = CardPayment(
            self.get_final_amount(), fail_reason
        )

    def process_card_payment(self) -> bool:
        result = self._active_payment.process()
        self._save_after_payment()
        self.cart.items = []
        self._active_payment = None
        self.log("카드 결제 완료")
        return result

    def cancel_payment(self) -> int:
        inserted = getattr(self._active_payment, "inserted_amount", 0)
        self._active_payment = None
        return inserted

    # ── 관리자 ─────────────────────────────────────────────────
    def authenticate_admin(self, pw: str) -> bool:
        from app.password_utils import verify_password
        stored = self.admin_config.get("password", "")
        if not verify_password(pw, stored):
            raise AdminAuthException("비밀번호가 올바르지 않습니다")
        return True

    def admin_replenish(self, ingredient_id: str, amount: int) -> None:
        self.ingredients[ingredient_id].replenish(amount)
        self._save_ingredients()

    def admin_set_price(self, product_id: str, price: int) -> None:
        for p in self.products:
            if p.product_id == product_id:
                p.base_price = price
                self._save_products()
                return
        raise KeyError(f"상품을 찾을 수 없습니다: {product_id}")

    def admin_toggle_product(self, product_id: str, flag: bool) -> None:
        for p in self.products:
            if p.product_id == product_id:
                p.is_available = flag
                self._save_products()
                return
        raise KeyError(f"상품을 찾을 수 없습니다: {product_id}")

    def admin_add_cash(self, denomination: int, count: int) -> None:
        self.change_reserve.add_cash(denomination, count)
        self.data_manager.save_change_reserve(
            {str(k): v for k, v in self.change_reserve.reserve.items()}
        )

    def admin_change_password(self, new_pw: str) -> None:
        self.admin_config["password"] = new_pw
        self.data_manager.save_admin_config(self.admin_config)

    # ── 내부 ──────────────────────────────────────────────────
    def _save_after_payment(self) -> None:
        self._save_ingredients()
        self.data_manager.save_change_reserve(
            {str(k): v for k, v in self.change_reserve.reserve.items()}
        )
        # self._update_stats()  # dead code

    def _save_ingredients(self) -> None:
        self.data_manager.save_ingredients([
            {"ingredient_id": i.ingredient_id, "name": i.name,
             "stock": i.stock, "max_capacity": i.max_capacity, "unit": i.unit}
            for i in self.ingredients.values()
        ])

    def _save_products(self) -> None:
        self.data_manager.save_products(self.products)

    # def _update_stats(self) -> None:  # dead code
    #     pass

    def log(self, msg: str) -> None:
        if self.logger:
            self.logger(msg)
