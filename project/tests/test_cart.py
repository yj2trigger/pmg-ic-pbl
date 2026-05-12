import unittest

from app.cart import OrderItem, Cart
from app.product import Coffee, CustomOption
from app.ingredient import Ingredient
from app.exceptions import InsufficientStockException


def _make_item(base_price: int, quantity: int) -> OrderItem:
    return OrderItem(Coffee("p1", "아메리카노", base_price), {}, quantity)


def _make_item_with_options(base_price: int, options: dict, quantity: int) -> OrderItem:
    return OrderItem(Coffee("p1", "아메리카노", base_price), options, quantity)


def _ing(stock: int) -> Ingredient:
    return Ingredient("coffee_bean", "원두", stock, 100)


def _opts(ing_dic: dict) -> dict:
    return {"size": CustomOption("size_large", "Large", 500, ing_dic)}


class TestOrderItem(unittest.TestCase):

    def test_order_item_subtotal(self):
        item = _make_item(3500, 2)
        self.assertEqual(item.calculate_subtotal(), 7000)

    def test_order_item_subtotal_qty_one(self):
        item = _make_item(3500, 1)
        self.assertEqual(item.calculate_subtotal(), 3500)

    def test_order_item_subtotal_with_options(self):
        # base 3000 + size 500 + shot 300 = 3800, qty 2 → 7600
        opts = {
            "size": CustomOption("size_large", "Large", 500),
            "shot": CustomOption("shot_2", "2샷", 300),
        }
        item = _make_item_with_options(3000, opts, 2)
        self.assertEqual(item.calculate_subtotal(), 7600)

    def test_order_item_subtotal_with_zero_extra(self):
        opts = {"temp": CustomOption("temp_hot", "HOT", 0)}
        item = _make_item_with_options(3000, opts, 1)
        self.assertEqual(item.calculate_subtotal(), 3000)

    def test_get_summary_no_options(self):
        item = _make_item(3000, 1)
        self.assertEqual(item.get_summary(), "아메리카노 × 1")

    def test_get_summary_with_options(self):
        opts = {
            "size": CustomOption("size_large", "Large", 500),
            "temp": CustomOption("temp_ice", "ICE", 0),
        }
        item = _make_item_with_options(3000, opts, 2)
        self.assertEqual(item.get_summary(), "아메리카노 / Large / ICE × 2")

    def test_get_summary_qty_reflected(self):
        item = _make_item(3000, 3)
        self.assertIn("× 3", item.get_summary())

    def test_get_required_ingredients_single_option(self):
        opts = {"size": CustomOption("size_large", "Large", 500, {"coffee_bean": 2, "water": 3})}
        item = _make_item_with_options(3000, opts, 1)
        self.assertEqual(item.get_required_ingredients(), {"coffee_bean": 2, "water": 3})

    def test_get_required_ingredients_multiple_options(self):
        opts = {
            "size": CustomOption("size_large", "Large", 500, {"coffee_bean": 2, "water": 3}),
            "shot": CustomOption("shot_2", "2샷", 300, {"coffee_bean": 1}),
            "temp": CustomOption("temp_ice", "ICE", 0, {"ice": 5}),
        }
        item = _make_item_with_options(3000, opts, 1)
        self.assertEqual(item.get_required_ingredients(), {"coffee_bean": 3, "water": 3, "ice": 5})

    def test_get_required_ingredients_no_options(self):
        item = _make_item(3000, 1)
        self.assertEqual(item.get_required_ingredients(), {})

    def test_can_fulfill_all_available(self):
        opts = {"size": CustomOption("size_large", "Large", 500, {"coffee_bean": 2, "water": 3})}
        item = _make_item_with_options(3000, opts, 1)
        ingredients = {
            "coffee_bean": Ingredient("coffee_bean", "원두", 10, 100),
            "water":       Ingredient("water", "물", 10, 100),
        }
        self.assertTrue(item.can_fulfill(ingredients))

    def test_can_fulfill_one_short(self):
        opts = {"size": CustomOption("size_large", "Large", 500, {"coffee_bean": 2, "water": 3})}
        item = _make_item_with_options(3000, opts, 1)
        ingredients = {
            "coffee_bean": Ingredient("coffee_bean", "원두", 1, 100),
            "water":       Ingredient("water", "물", 10, 100),
        }
        self.assertFalse(item.can_fulfill(ingredients))

    def test_can_fulfill_exact_stock(self):
        opts = {"size": CustomOption("size_large", "Large", 500, {"coffee_bean": 2, "water": 3})}
        item = _make_item_with_options(3000, opts, 1)
        ingredients = {
            "coffee_bean": Ingredient("coffee_bean", "원두", 2, 100),
            "water":       Ingredient("water", "물", 3, 100),
        }
        self.assertTrue(item.can_fulfill(ingredients))

    def test_can_fulfill_empty_options(self):
        item = _make_item(3000, 1)
        ingredients = {"coffee_bean": Ingredient("coffee_bean", "원두", 0, 100)}
        self.assertTrue(item.can_fulfill(ingredients))


class TestCart(unittest.TestCase):

    def setUp(self):
        self.cart = Cart()

    def test_cart_add_item(self):
        self.cart.add_item(_make_item(3000, 1), {})
        self.assertEqual(len(self.cart.items), 1)

    def test_cart_add_multiple(self):
        for _ in range(3):
            self.cart.add_item(_make_item(3000, 1), {})
        self.assertEqual(len(self.cart.items), 3)

    def test_cart_remove_item(self):
        item_a = _make_item(3000, 1)
        item_b = _make_item(5000, 1)
        self.cart.add_item(item_a, {})
        self.cart.add_item(item_b, {})
        self.cart.remove_item(0, {})
        self.assertEqual(len(self.cart.items), 1)
        self.assertIs(self.cart.items[0], item_b)

    def test_cart_get_subtotal(self):
        self.cart.add_item(_make_item(3000, 1), {})
        self.cart.add_item(_make_item(5000, 1), {})
        self.assertEqual(self.cart.get_subtotal(), 8000)

    def test_cart_get_subtotal_empty(self):
        self.assertEqual(self.cart.get_subtotal(), 0)

    def test_cart_is_empty_true(self):
        self.assertTrue(self.cart.is_empty())

    def test_cart_is_empty_false(self):
        self.cart.add_item(_make_item(3000, 1), {})
        self.assertFalse(self.cart.is_empty())

    def test_cart_clear(self):
        for _ in range(3):
            self.cart.add_item(_make_item(3000, 1), {})
        self.cart.clear({})
        self.assertEqual(self.cart.items, [])

    def test_cart_update_quantity(self):
        self.cart.add_item(_make_item(3000, 2), {})
        self.cart.update_quantity(0, 5, {})
        self.assertEqual(self.cart.get_subtotal(), 15000)

    def test_cart_get_subtotal_with_options(self):
        opts = {"size": CustomOption("size_large", "Large", 500)}
        self.cart.add_item(_make_item_with_options(3000, opts, 1), {})
        self.cart.add_item(_make_item(2000, 2), {})
        self.assertEqual(self.cart.get_subtotal(), 7500)

    def test_cart_update_quantity_with_options(self):
        opts = {"size": CustomOption("size_large", "Large", 500)}
        self.cart.add_item(_make_item_with_options(3000, opts, 1), {})
        self.cart.update_quantity(0, 3, {})
        self.assertEqual(self.cart.get_subtotal(), 10500)

    # add_item 재고 검증
    def test_add_item_deducts_stock(self):
        ing = _ing(10)
        self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 1), {"coffee_bean": ing})
        self.assertEqual(ing.stock, 8)  # 10 - 2×1

    def test_add_item_deducts_stock_with_quantity(self):
        ing = _ing(10)
        self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 3), {"coffee_bean": ing})
        self.assertEqual(ing.stock, 4)  # 10 - 2×3

    def test_add_item_raises_when_insufficient(self):
        ingredients = {"coffee_bean": _ing(1)}  # 보유 1, 필요 2
        with self.assertRaises(InsufficientStockException):
            self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 1), ingredients)

    def test_add_item_not_appended_when_insufficient(self):
        ingredients = {"coffee_bean": _ing(1)}
        try:
            self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 1), ingredients)
        except InsufficientStockException:
            pass
        self.assertTrue(self.cart.is_empty())

    # remove_item 재고 복원
    def test_remove_item_replenishes_stock(self):
        ing = _ing(10)
        ingredients = {"coffee_bean": ing}
        self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 1), ingredients)
        self.assertEqual(ing.stock, 8)
        self.cart.remove_item(0, ingredients)
        self.assertEqual(ing.stock, 10)  # 복원

    def test_remove_item_replenishes_stock_with_quantity(self):
        ing = _ing(10)
        ingredients = {"coffee_bean": ing}
        self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 3), ingredients)
        self.assertEqual(ing.stock, 4)   # 10 - 2×3
        self.cart.remove_item(0, ingredients)
        self.assertEqual(ing.stock, 10)  # 4 + 2×3 복원

    # update_quantity 재고 조정
    def test_update_quantity_increase_deducts(self):
        ing = _ing(10)
        ingredients = {"coffee_bean": ing}
        self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 1), ingredients)
        self.assertEqual(ing.stock, 8)
        self.cart.update_quantity(0, 3, ingredients)  # 1 → 3, delta=2
        self.assertEqual(ing.stock, 4)  # 8 - 2×2

    def test_update_quantity_decrease_replenishes(self):
        ing = _ing(10)
        ingredients = {"coffee_bean": ing}
        self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 3), ingredients)
        self.assertEqual(ing.stock, 4)
        self.cart.update_quantity(0, 1, ingredients)  # 3 → 1, delta=-2
        self.assertEqual(ing.stock, 8)  # 4 + 2×2 복원

    def test_update_quantity_same_no_change(self):
        ing = _ing(10)
        ingredients = {"coffee_bean": ing}
        self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 2), ingredients)
        self.assertEqual(ing.stock, 6)
        self.cart.update_quantity(0, 2, ingredients)  # delta=0
        self.assertEqual(ing.stock, 6)  # 변화 없음

    # clear 재고 복원
    def test_clear_replenishes_all_stock(self):
        ing = _ing(20)
        ingredients = {"coffee_bean": ing}
        self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 2}), 2), ingredients)
        self.cart.add_item(_make_item_with_options(3000, _opts({"coffee_bean": 3}), 1), ingredients)
        self.assertEqual(ing.stock, 13)  # 20 - 2×2 - 3×1
        self.cart.clear(ingredients)
        self.assertEqual(ing.stock, 20)  # 전부 복원


if __name__ == "__main__":
    unittest.main(verbosity=2)
