import unittest

from app.stats import Statistics
from app.cart import OrderItem
from app.product import Coffee, Gummy, CustomOption


def _item(product_type: str, quantity: int, ing_dic: dict = {}) -> OrderItem:
    if product_type == "coffee":
        product = Coffee("p1", "아메리카노", 3000)
    else:
        product = Gummy("p2", "구미", 2000)
    opts = {"opt": CustomOption("o1", "옵션", 0, ing_dic)} if ing_dic else {}
    return OrderItem(product, opts, quantity)


class TestStatistics(unittest.TestCase):

    def setUp(self):
        self.stats = Statistics()

    def test_record_sales_increment(self):
        self.stats.record([_item("coffee", 1)], 3000)
        self.assertEqual(self.stats.sales["coffee"], 1)

    def test_record_revenue_increment(self):
        self.stats.record([_item("coffee", 1)], 4500)
        self.assertEqual(self.stats.revenue, 4500)

    def test_record_ingredient_increment(self):
        self.stats.record([_item("coffee", 1, {"coffee_bean": 1})], 3000)
        self.assertEqual(self.stats.ingredients_used["coffee_bean"], 1)

    def test_record_multiple(self):
        self.stats.record([_item("coffee", 2)], 6000)
        self.stats.record([_item("coffee", 1)], 3000)
        self.stats.record([_item("gummy", 1)], 2000)
        self.assertEqual(self.stats.sales["coffee"], 3)
        self.assertEqual(self.stats.sales["gummy"], 1)
        self.assertEqual(self.stats.revenue, 11000)

    def test_get_popular_order(self):
        self.stats.record([_item("coffee", 3)], 9000)
        self.stats.record([_item("gummy", 1)], 2000)
        popular = self.stats.get_popular(2)
        self.assertEqual(popular[0][0], "coffee")

    def test_get_popular_n_limit(self):
        for ptype in ["coffee", "gummy"]:
            self.stats.record([_item(ptype, 1)], 3000)
        self.assertEqual(len(self.stats.get_popular(1)), 1)

    def test_get_popular_n_exceeds(self):
        self.stats.record([_item("coffee", 1)], 3000)
        self.stats.record([_item("gummy", 1)], 2000)
        self.assertEqual(len(self.stats.get_popular(5)), 2)

    def test_hot_above_threshold(self):
        self.stats.record([_item("coffee", 4, {"coffee_bean": 1})], 12000)
        # total_orders=4, coffee_bean=4 → ratio=1.0 >= 0.3
        self.assertIn("coffee_bean", self.stats.get_hot_ingredients(0.3))

    def test_hot_below_threshold(self):
        self.stats.record([_item("coffee", 1, {"coffee_bean": 1})], 3000)
        self.stats.record([_item("gummy", 4)], 8000)
        # total_orders=5, coffee_bean=1 → ratio=0.2 < 0.3
        self.assertNotIn("coffee_bean", self.stats.get_hot_ingredients(0.3))

    def test_hot_exact_threshold(self):
        self.stats.record([_item("coffee", 3, {"coffee_bean": 1})], 9000)
        self.stats.record([_item("gummy", 7)], 14000)
        # total_orders=10, coffee_bean=3 → ratio=0.3 >= 0.3
        self.assertIn("coffee_bean", self.stats.get_hot_ingredients(0.3))

    def test_hot_no_orders(self):
        result = self.stats.get_hot_ingredients(0.3)
        self.assertEqual(result, [])

    def test_serialization_roundtrip(self):
        self.stats.record([_item("coffee", 2, {"coffee_bean": 1})], 6000)
        restored = Statistics.from_dict(self.stats.to_dict())
        self.assertEqual(restored.sales, self.stats.sales)
        self.assertEqual(restored.ingredients_used, self.stats.ingredients_used)
        self.assertEqual(restored.revenue, self.stats.revenue)


if __name__ == "__main__":
    unittest.main(verbosity=2)
