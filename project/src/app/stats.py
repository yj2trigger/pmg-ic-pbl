class Statistics:
    def __init__(self):
        self.sales: dict = {}            # {medicine_id: count}
        self.ingredients_used: dict = {} # {ingredient_id: count}
        self.revenue: int = 0

    def record(self, order_items: list, amount: int) -> None:
        for item in order_items:
            product_key = self._get_product_key(item.product)
            self.sales[product_key] = self.sales.get(product_key, 0) + item.quantity
            for ingredient_id, unit_qty in item.get_required_ingredients().items():
                used = unit_qty * item.quantity
                self.ingredients_used[ingredient_id] = (
                    self.ingredients_used.get(ingredient_id, 0) + used
                )
        self.revenue += amount

    def _get_product_key(self, product) -> str:
        for attr in ("medicine_id", "product_id", "product_type"):
            value = getattr(product, attr, None)
            if value:
                return value
        return product.get_display_name()

    def get_popular(self, n: int) -> list:
        sorted_sales = sorted(self.sales.items(), key=lambda x: x[1], reverse=True)
        return sorted_sales[:n]

    def get_hot_ingredients(self, threshold: float) -> list:
        total_orders = sum(self.sales.values())
        if total_orders == 0:
            return []
        return [
            ingredient_id
            for ingredient_id, count in self.ingredients_used.items()
            if count / total_orders >= threshold
        ]

    def to_dict(self) -> dict:
        return {
            "sales": self.sales,
            "ingredients_used": self.ingredients_used,
            "revenue": self.revenue,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Statistics":
        obj = cls()
        obj.sales = data.get("sales", {})
        obj.ingredients_used = data.get("ingredients_used", {})
        obj.revenue = data.get("revenue", 0)
        return obj
