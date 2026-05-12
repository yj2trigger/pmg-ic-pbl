import unittest

from app.product import CustomOption, OptionGroup, Coffee, Gummy


class TestCustomOption(unittest.TestCase):

    def test_option_extra_price(self):
        opt = CustomOption("opt1", "Large", 500)
        self.assertEqual(opt.get_extra_price(), 500)


class TestProduct(unittest.TestCase):

    def test_calculate_price_no_options(self):
        product = Coffee("p1", "아메리카노", 3000)
        self.assertEqual(product.calculate_price({}), 3000)

    def test_calculate_price_with_options(self):
        opt1 = CustomOption("opt1", "Large", 500)
        opt2 = CustomOption("opt2", "2샷", 300)
        product = Coffee("p1", "아메리카노", 3000)
        self.assertEqual(product.calculate_price({"size": opt1, "shot": opt2}), 3800)


class TestOptionGroup(unittest.TestCase):

    def test_cream_active_for_latte(self):
        group = OptionGroup("cream", "크림", [], active_for=["latte", "cappuccino"])
        self.assertTrue(group.is_active_for("latte"))

    def test_cream_inactive_for_americano(self):
        group = OptionGroup("cream", "크림", [], active_for=["latte", "cappuccino"])
        self.assertFalse(group.is_active_for("americano"))
 

if __name__ == "__main__":
    unittest.main(verbosity=2)
