import unittest

from app.exceptions import (
    KioskException,
    StockOverflowException,
    InsufficientStockException,
    InsufficientChangeException,
    PaymentException,
    AdminAuthException,
    InvalidRecipeException,
)


class TestKioskException(unittest.TestCase):

    def test_TC_EX_01_raise_and_catch_with_message(self):
        with self.assertRaises(KioskException) as ctx:
            raise KioskException("test")
        self.assertEqual(str(ctx.exception), "test")

    def test_TC_EX_02_is_subclass_of_exception(self):
        self.assertTrue(issubclass(KioskException, Exception))

    def test_TC_EX_03_instantiate_without_message(self):
        e = KioskException()
        self.assertIsInstance(e, KioskException)


class TestSubclassInheritance(unittest.TestCase):

    def test_TC_EX_04_stock_overflow_is_kiosk_exception(self):
        self.assertTrue(issubclass(StockOverflowException, KioskException))

    def test_TC_EX_05_insufficient_stock_is_kiosk_exception(self):
        self.assertTrue(issubclass(InsufficientStockException, KioskException))

    def test_TC_EX_06_insufficient_change_is_kiosk_exception(self):
        self.assertTrue(issubclass(InsufficientChangeException, KioskException))

    def test_TC_EX_07_payment_is_kiosk_exception(self):
        self.assertTrue(issubclass(PaymentException, KioskException))

    def test_TC_EX_08_admin_auth_is_kiosk_exception(self):
        self.assertTrue(issubclass(AdminAuthException, KioskException))

    def test_TC_EX_09_invalid_recipe_is_kiosk_exception(self):
        self.assertTrue(issubclass(InvalidRecipeException, KioskException))


class TestSubclassRaiseCatch(unittest.TestCase):

    def test_TC_EX_10_stock_overflow_raise_catch(self):
        with self.assertRaises(StockOverflowException):
            raise StockOverflowException("재고 초과")

    def test_TC_EX_11_insufficient_stock_raise_catch(self):
        with self.assertRaises(InsufficientStockException):
            raise InsufficientStockException("재고 부족")

    def test_TC_EX_12_insufficient_change_raise_catch(self):
        with self.assertRaises(InsufficientChangeException):
            raise InsufficientChangeException("잔돈 부족")

    def test_TC_EX_13_payment_raise_catch(self):
        with self.assertRaises(PaymentException):
            raise PaymentException("결제 실패")

    def test_TC_EX_14_admin_auth_raise_catch(self):
        with self.assertRaises(AdminAuthException):
            raise AdminAuthException("인증 실패")

    def test_TC_EX_15_invalid_recipe_raise_catch(self):
        with self.assertRaises(InvalidRecipeException):
            raise InvalidRecipeException("형식 오류")


class TestPolymorphism(unittest.TestCase):

    def _raises_caught_as_kiosk(self, exc_class):
        try:
            raise exc_class("test")
        except KioskException:
            return True
        return False

    def test_TC_EX_16_all_subclasses_caught_as_kiosk_exception(self):
        subclasses = [
            StockOverflowException,
            InsufficientStockException,
            InsufficientChangeException,
            PaymentException,
            AdminAuthException,
            InvalidRecipeException,
        ]
        for cls in subclasses:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(self._raises_caught_as_kiosk(cls))


if __name__ == "__main__":
    unittest.main(verbosity=2)
