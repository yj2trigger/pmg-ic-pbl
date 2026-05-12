#관리자가 인스턴스 생성

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
