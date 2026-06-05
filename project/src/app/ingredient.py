# ──────────────────────────────────────────────────────────────────────────────
# ingredient.py — 아이스크림 재료 도메인 클래스
#
# [역할]
#   Ingredient: 재료 ID·이름·재고·최대 용량을 보관하고
#   재고 차감(deduct)·보충(replenish)·가용 여부(is_available) 연산을 제공한다.
#
# [재고 차감 시점]
#   Cart.add_item() 호출 시 즉시 차감. 결제 완료가 아니라 장바구니 추가 시점에 차감한다.
#   이유: 동시 접근 없는 단일 키오스크지만, 재고 부족 옵션을 즉시 비활성화하기 위해.
#   세션 포기 시 Cart.clear() → replenish()로 복원된다.
#
# [의존성]
#   import: app.exceptions (InsufficientStockException, StockOverflowException)
#   이 파일을 사용하는 곳:
#     data_manager.py → load_ingredients()에서 Ingredient(**item) 생성
#     cart.py → add_item(), remove_item(), update_quantity(), clear()
#     kiosk_controller.py → admin_replenish()
# ──────────────────────────────────────────────────────────────────────────────

from app.exceptions import InsufficientStockException, StockOverflowException

class Ingredient:
    def __init__(self, ingredient_id: str, name: str, stock: int, max_capacity: int, unit: str = "개"):
        self.ingredient_id = ingredient_id
        self.name = name
        self.stock = stock
        self.max_capacity = max_capacity
        self.unit = unit

    def is_available(self, needed: int) -> bool:
        return self.stock >= needed

    def deduct(self, amount: int) -> None:
        if self.stock < amount:
            raise InsufficientStockException(
                f"{self.name}: 재고 부족 (보유 {self.stock}, 필요 {amount})"
            )
        self.stock -= amount

    def replenish(self, amount: int) -> None:
        if self.stock + amount > self.max_capacity:
            raise StockOverflowException(
                f"{self.name}: 최대 용량 초과 (현재 {self.stock}, 추가 {amount}, 최대 {self.max_capacity})"
            )
        self.stock += amount

    def remaining_capacity(self) -> int:
        return self.max_capacity - self.stock

    def is_out_of_stock(self) -> bool:
        return self.stock == 0
