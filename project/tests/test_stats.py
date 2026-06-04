import unittest

from app.cart import OrderItem
from app.ice_cream import IceCreamProduct
from app.option import Option
from app.stats import Statistics


def _item(product_type: str, quantity: int, ing_dic: dict = {}) -> OrderItem:
    product = IceCreamProduct("p1", "아이스크림", 3000, True, product_type)
    opts = {"opt": Option("o1", "옵션", 0, ing_dic)} if ing_dic else {}
    return OrderItem(product, opts, quantity)


class TestStatistics(unittest.TestCase):

    def setUp(self):
        self.stats = Statistics()

    def test_record_sales_increment(self):
        self.stats.record([_item("stick", 1)], 3000)
        self.assertEqual(self.stats.sales["stick"], 1)

    def test_record_revenue_increment(self):
        self.stats.record([_item("stick", 1)], 4500)
        self.assertEqual(self.stats.revenue, 4500)

    def test_record_ingredient_increment(self):
        self.stats.record([_item("stick", 1, {"stick_base": 1})], 3000)
        self.assertEqual(self.stats.ingredients_used["stick_base"], 1)

    def test_record_multiple(self):
        self.stats.record([_item("stick", 2)], 6000)
        self.stats.record([_item("stick", 1)], 3000)
        self.stats.record([_item("scoop", 1)], 2000)
        self.assertEqual(self.stats.sales["stick"], 3)
        self.assertEqual(self.stats.sales["scoop"], 1)
        self.assertEqual(self.stats.revenue, 11000)

    def test_get_popular_order(self):
        self.stats.record([_item("stick", 3)], 9000)
        self.stats.record([_item("scoop", 1)], 2000)
        popular = self.stats.get_popular(2)
        self.assertEqual(popular[0][0], "stick")

    def test_get_popular_n_limit(self):
        for ptype in ["stick", "scoop"]:
            self.stats.record([_item(ptype, 1)], 3000)
        self.assertEqual(len(self.stats.get_popular(1)), 1)

    def test_get_popular_n_exceeds(self):
        self.stats.record([_item("stick", 1)], 3000)
        self.stats.record([_item("scoop", 1)], 2000)
        self.assertEqual(len(self.stats.get_popular(5)), 2)

    def test_hot_above_threshold(self):
        self.stats.record([_item("stick", 4, {"stick_base": 1})], 12000)
        # total_orders=4, stick_base=4 → ratio=1.0 >= 0.3
        self.assertIn("stick_base", self.stats.get_hot_ingredients(0.3))

    def test_hot_below_threshold(self):
        self.stats.record([_item("stick", 1, {"stick_base": 1})], 3000)
        self.stats.record([_item("scoop", 4)], 8000)
        # total_orders=5, stick_base=1 → ratio=0.2 < 0.3
        self.assertNotIn("stick_base", self.stats.get_hot_ingredients(0.3))

    def test_hot_exact_threshold(self):
        self.stats.record([_item("stick", 3, {"stick_base": 1})], 9000)
        self.stats.record([_item("scoop", 7)], 14000)
        # total_orders=10, stick_base=3 → ratio=0.3 >= 0.3
        self.assertIn("stick_base", self.stats.get_hot_ingredients(0.3))

    def test_hot_no_orders(self):
        result = self.stats.get_hot_ingredients(0.3)
        self.assertEqual(result, [])

    def test_serialization_roundtrip(self):
        self.stats.record([_item("stick", 2, {"stick_base": 1})], 6000)
        restored = Statistics.from_dict(self.stats.to_dict())
        self.assertEqual(restored.sales, self.stats.sales)
        self.assertEqual(restored.ingredients_used, self.stats.ingredients_used)
        self.assertEqual(restored.revenue, self.stats.revenue)


if __name__ == "__main__":
    unittest.main(verbosity=2)
