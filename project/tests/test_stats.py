import unittest

from app.cart import OrderItem
from app.medicine import Medicine
from app.stats import Statistics


class _Option:
    def __init__(self, required_ingredients_dic: dict):
        self.name = "옵션"
        self.required_ingredients_dic = required_ingredients_dic


def _item(medicine_id: str, quantity: int, ing_dic: dict | None = None) -> OrderItem:
    medicine = Medicine(medicine_id, medicine_id, 3000, True, ["두통"])
    opts = {"opt": _Option(ing_dic)} if ing_dic else {}
    return OrderItem(medicine, opts, quantity)


class TestStatistics(unittest.TestCase):

    def setUp(self):
        self.stats = Statistics()

    def test_record_sales_increment(self):
        self.stats.record([_item("MED-001", 1)], 3000)
        self.assertEqual(self.stats.sales["MED-001"], 1)

    def test_record_revenue_increment(self):
        self.stats.record([_item("MED-001", 1)], 4500)
        self.assertEqual(self.stats.revenue, 4500)

    def test_record_ingredient_increment(self):
        self.stats.record([_item("MED-001", 1, {"vitamin_c": 1})], 3000)
        self.assertEqual(self.stats.ingredients_used["vitamin_c"], 1)

    def test_record_multiple(self):
        self.stats.record([_item("MED-001", 2)], 6000)
        self.stats.record([_item("MED-001", 1)], 3000)
        self.stats.record([_item("MED-002", 1)], 2000)
        self.assertEqual(self.stats.sales["MED-001"], 3)
        self.assertEqual(self.stats.sales["MED-002"], 1)
        self.assertEqual(self.stats.revenue, 11000)

    def test_get_popular_order(self):
        self.stats.record([_item("MED-001", 3)], 9000)
        self.stats.record([_item("MED-002", 1)], 2000)
        popular = self.stats.get_popular(2)
        self.assertEqual(popular[0][0], "MED-001")

    def test_get_popular_n_limit(self):
        for medicine_id in ["MED-001", "MED-002"]:
            self.stats.record([_item(medicine_id, 1)], 3000)
        self.assertEqual(len(self.stats.get_popular(1)), 1)

    def test_get_popular_n_exceeds(self):
        self.stats.record([_item("MED-001", 1)], 3000)
        self.stats.record([_item("MED-002", 1)], 2000)
        self.assertEqual(len(self.stats.get_popular(5)), 2)

    def test_hot_above_threshold(self):
        self.stats.record([_item("MED-001", 4, {"vitamin_c": 1})], 12000)
        # total_orders=4, vitamin_c=4 -> ratio=1.0 >= 0.3
        self.assertIn("vitamin_c", self.stats.get_hot_ingredients(0.3))

    def test_hot_below_threshold(self):
        self.stats.record([_item("MED-001", 1, {"vitamin_c": 1})], 3000)
        self.stats.record([_item("MED-002", 4)], 8000)
        # total_orders=5, vitamin_c=1 -> ratio=0.2 < 0.3
        self.assertNotIn("vitamin_c", self.stats.get_hot_ingredients(0.3))

    def test_hot_exact_threshold(self):
        self.stats.record([_item("MED-001", 3, {"vitamin_c": 1})], 9000)
        self.stats.record([_item("MED-002", 7)], 14000)
        # total_orders=10, vitamin_c=3 -> ratio=0.3 >= 0.3
        self.assertIn("vitamin_c", self.stats.get_hot_ingredients(0.3))

    def test_hot_no_orders(self):
        result = self.stats.get_hot_ingredients(0.3)
        self.assertEqual(result, [])

    def test_serialization_roundtrip(self):
        self.stats.record([_item("MED-001", 2, {"vitamin_c": 1})], 6000)
        restored = Statistics.from_dict(self.stats.to_dict())
        self.assertEqual(restored.sales, self.stats.sales)
        self.assertEqual(restored.ingredients_used, self.stats.ingredients_used)
        self.assertEqual(restored.revenue, self.stats.revenue)


if __name__ == "__main__":
    unittest.main(verbosity=2)
