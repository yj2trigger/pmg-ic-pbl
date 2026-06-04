import unittest

from app.cart import OrderItem, Cart
from app.ice_cream import IceCreamProduct


def _make_product(price: int = 3000) -> IceCreamProduct:
    return IceCreamProduct("p1", "스틱 아이스크림", price, True, "stick")


def _make_item(price: int = 3000, qty: int = 1) -> OrderItem:
    return OrderItem(_make_product(price), {}, qty)


class TestOrderItem(unittest.TestCase):

    def test_subtotal_single(self):
        self.assertEqual(_make_item(3000, 1).calculate_subtotal(), 3000)

    def test_subtotal_multiple(self):
        self.assertEqual(_make_item(3500, 2).calculate_subtotal(), 7000)

    def test_get_summary_no_options(self):
        self.assertEqual(_make_item(3000, 1).get_summary(), "스틱 아이스크림 × 1")

    def test_get_summary_qty_three(self):
        self.assertIn("× 3", _make_item(3000, 3).get_summary())

    def test_get_required_ingredients_empty(self):
        self.assertEqual(_make_item().get_required_ingredients(), {})

    def test_can_fulfill_no_ingredients(self):
        self.assertTrue(_make_item().can_fulfill({}))


class TestCart(unittest.TestCase):

    def setUp(self):
        self.cart = Cart()

    def test_add_item(self):
        self.cart.add_item(_make_item(), {})
        self.assertEqual(len(self.cart.items), 1)

    def test_add_multiple(self):
        for _ in range(3):
            self.cart.add_item(_make_item(), {})
        self.assertEqual(len(self.cart.items), 3)

    def test_remove_item(self):
        a, b = _make_item(3000), _make_item(5000)
        self.cart.add_item(a, {})
        self.cart.add_item(b, {})
        self.cart.remove_item(0, {})
        self.assertEqual(len(self.cart.items), 1)
        self.assertIs(self.cart.items[0], b)

    def test_get_subtotal(self):
        self.cart.add_item(_make_item(3000), {})
        self.cart.add_item(_make_item(5000), {})
        self.assertEqual(self.cart.get_subtotal(), 8000)

    def test_get_subtotal_empty(self):
        self.assertEqual(self.cart.get_subtotal(), 0)

    def test_is_empty_true(self):
        self.assertTrue(self.cart.is_empty())

    def test_is_empty_false(self):
        self.cart.add_item(_make_item(), {})
        self.assertFalse(self.cart.is_empty())

    def test_clear(self):
        for _ in range(3):
            self.cart.add_item(_make_item(), {})
        self.cart.clear({})
        self.assertEqual(self.cart.items, [])

    def test_update_quantity_increase(self):
        self.cart.add_item(_make_item(3000, 2), {})
        self.cart.update_quantity(0, 5, {})
        self.assertEqual(self.cart.get_subtotal(), 15000)

    def test_update_quantity_decrease(self):
        self.cart.add_item(_make_item(3000, 3), {})
        self.cart.update_quantity(0, 1, {})
        self.assertEqual(self.cart.get_subtotal(), 3000)

    def test_update_quantity_same(self):
        self.cart.add_item(_make_item(3000, 2), {})
        self.cart.update_quantity(0, 2, {})
        self.assertEqual(self.cart.get_subtotal(), 6000)

    def test_subtotal_with_quantity(self):
        self.cart.add_item(_make_item(4000, 3), {})
        self.assertEqual(self.cart.get_subtotal(), 12000)

    def test_add_multiple_different_items(self):
        self.cart.add_item(_make_item(3000, 1), {})
        self.cart.add_item(_make_item(2500, 2), {})
        self.assertEqual(self.cart.get_subtotal(), 8000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
