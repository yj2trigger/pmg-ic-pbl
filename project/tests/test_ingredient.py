import unittest

from app.ingredient import Ingredient
from app.exceptions import InsufficientStockException, StockOverflowException


class TestIngredient(unittest.TestCase):

    def test_deduct_normal(self):
        ing = Ingredient("i1", "원두", 100, 200)
        ing.deduct(30)
        self.assertEqual(ing.stock, 70)

    def test_deduct_exact(self):
        ing = Ingredient("i1", "원두", 50, 200)
        ing.deduct(50)
        self.assertEqual(ing.stock, 0)

    def test_deduct_insufficient(self):
        ing = Ingredient("i1", "원두", 30, 200)
        with self.assertRaises(InsufficientStockException):
            ing.deduct(31)

    def test_deduct_zero(self):
        ing = Ingredient("i1", "원두", 50, 200)
        ing.deduct(0)
        self.assertEqual(ing.stock, 50)

    def test_replenish_normal(self):
        ing = Ingredient("i1", "원두", 50, 100)
        ing.replenish(30)
        self.assertEqual(ing.stock, 80)

    def test_replenish_to_max(self):
        ing = Ingredient("i1", "원두", 90, 100)
        ing.replenish(10)
        self.assertEqual(ing.stock, 100)

    def test_replenish_overflow(self):
        ing = Ingredient("i1", "원두", 90, 100)
        with self.assertRaises(StockOverflowException):
            ing.replenish(11)

    def test_is_available_true(self):
        ing = Ingredient("i1", "원두", 50, 200)
        self.assertTrue(ing.is_available(50))

    def test_is_available_false(self):
        ing = Ingredient("i1", "원두", 50, 200)
        self.assertFalse(ing.is_available(51))

    def test_is_out_of_stock_true(self):
        ing = Ingredient("i1", "원두", 0, 200)
        self.assertTrue(ing.is_out_of_stock())

    def test_is_out_of_stock_false(self):
        ing = Ingredient("i1", "원두", 1, 200)
        self.assertFalse(ing.is_out_of_stock())

    def test_remaining_capacity(self):
        ing = Ingredient("i1", "원두", 30, 100)
        self.assertEqual(ing.remaining_capacity(), 70)


if __name__ == "__main__":
    unittest.main(verbosity=2)
