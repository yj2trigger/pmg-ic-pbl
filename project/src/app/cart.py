# ──────────────────────────────────────────────────────────────────────────────
# cart.py — 장바구니 도메인 (OrderItem + Cart)
#
# [역할]
#   OrderItem: 상품 1종의 옵션·수량·가격 계산·재료 소비량 계산을 담당한다.
#   Cart: OrderItem 목록 관리. add/remove/update 시 Ingredient 재고를 즉시 반영한다.
#
# [재고 차감 설계 원칙]
#   재고는 장바구니에 추가하는 시점(add_item)에 차감하고,
#   수량 변경(update_quantity)은 델타(delta)만 추가/복원 — 전체 재계산 없이 최소 변경.
#   세션 포기·삭제·수량 감소 시 replenish()로 복원.
#
# [의존성]
#   import: app.exceptions (InsufficientStockException)
#   이 파일을 사용하는 곳:
#     kiosk_controller.py → add_to_cart(), remove_from_cart(), update_cart_qty()
#     main_window.py → cart.items 직접 접근 (리팩터링 대상)
# ──────────────────────────────────────────────────────────────────────────────

from app.exceptions import InsufficientStockException

class OrderItem: # 한종류 상품의 총 가격과 구매 내역
    def __init__(self, product, selected_options: dict, quantity: int):
        self.product = product
        self.selected_options = selected_options # opts = {"size": CustomOption("size_large", "Large", 500)}
        self.quantity = quantity

    def calculate_subtotal(self) -> int:
        return self.product.calculate_price(self.selected_options) * self.quantity

    def get_summary(self) -> str:
        parts = [self.product.get_display_name()]
        parts += [opt.name for opt in self.selected_options.values()]
        return " / ".join(parts) + f" × {self.quantity}"

    def get_required_ingredients(self) -> dict:
        total = {}
        for option in self.selected_options.values():
            for ingredient_id, qty in option.required_ingredients_dic.items():
                total[ingredient_id] = total.get(ingredient_id, 0) + qty
        return total

    def can_fulfill(self, ingredients: dict) -> bool:
        for ingredient_id, unit_qty in self.get_required_ingredients().items():
            ingredient = ingredients.get(ingredient_id)
            if ingredient is None or not ingredient.is_available(unit_qty * self.quantity):
                return False
        return True


class Cart:
    def __init__(self):
        self.items: list = []

    def add_item(self, item: OrderItem, ingredients: dict) -> None:
        if not item.can_fulfill(ingredients):
            raise InsufficientStockException("재고 부족으로 장바구니에 추가할 수 없습니다")
        for ingredient_id, unit_qty in item.get_required_ingredients().items():
            ingredients[ingredient_id].deduct(unit_qty * item.quantity)
        self.items.append(item)

    def remove_item(self, index: int, ingredients: dict) -> None:
        item = self.items[index]
        for ingredient_id, unit_qty in item.get_required_ingredients().items():
            ingredients[ingredient_id].replenish(unit_qty * item.quantity)
        del self.items[index]

    def update_quantity(self, index: int, qty: int, ingredients: dict) -> None:
        item = self.items[index]
        delta = qty - item.quantity
        for ingredient_id, unit_qty in item.get_required_ingredients().items():
            if delta > 0:
                ingredients[ingredient_id].deduct(unit_qty * delta)
            elif delta < 0:
                ingredients[ingredient_id].replenish(unit_qty * abs(delta))
        item.quantity = qty

    def get_subtotal(self) -> int:
        return sum(item.calculate_subtotal() for item in self.items)

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def clear(self, ingredients: dict) -> None:
        for item in self.items:
            for ingredient_id, unit_qty in item.get_required_ingredients().items():
                ingredients[ingredient_id].replenish(unit_qty * item.quantity)
        self.items = []
