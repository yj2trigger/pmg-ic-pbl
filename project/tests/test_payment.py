import unittest

from app.payment import ChangeReserve, CashPayment, CardPayment
from app.exceptions import InsufficientChangeException, PaymentException


def _reserve(override: dict | None = None) -> ChangeReserve:
    base = {50000: 0, 10000: 0, 5000: 0, 1000: 0}
    if override:
        base.update(override)
    return ChangeReserve(base)


class TestChangeReserve(unittest.TestCase):

    def test_dispense_normal(self):
        # 6000원 잔돈: 5000×1 + 1000×1
        r = _reserve({5000: 1, 1000: 5})
        self.assertEqual(r.dispense(6000), {5000: 1, 1000: 1})

    def test_dispense_exact_denomination(self):
        r = _reserve({5000: 1})
        self.assertEqual(r.dispense(5000), {5000: 1})

    def test_dispense_no_large_use_small(self):
        # 5000원 필요, 5000원 없음 → 1000원 5개
        r = _reserve({5000: 0, 1000: 10})
        self.assertEqual(r.dispense(5000), {1000: 5})

    def test_dispense_zero_change(self):
        r = _reserve({1000: 5})
        self.assertEqual(r.dispense(0), {})
        self.assertEqual(r.reserve[1000], 5)  # reserve 변화 없음

    def test_dispense_insufficient(self):
        # 1000원 3개(3000원) 보유, 5000원 필요
        r = _reserve({1000: 3})
        with self.assertRaises(InsufficientChangeException):
            r.dispense(5000)

    def test_dispense_updates_reserve(self):
        r = _reserve({5000: 1, 1000: 5})
        r.dispense(6000)
        self.assertEqual(r.reserve[5000], 0)
        self.assertEqual(r.reserve[1000], 4)

    def test_can_make_change_true(self):
        r = _reserve({1000: 2})
        self.assertTrue(r.can_make_change(2000))

    def test_can_make_change_false(self):
        # 1000원 3개(3000원) 보유, 5000원 반환 불가
        r = _reserve({1000: 3})
        self.assertFalse(r.can_make_change(5000))

    def test_can_make_change_zero(self):
        self.assertTrue(_reserve().can_make_change(0))

    def test_dispense_reserve_unchanged_on_failure(self):
        r = _reserve({1000: 3})
        try:
            r.dispense(5000)
        except InsufficientChangeException:
            pass
        self.assertEqual(r.reserve[1000], 3)  # 실패해도 reserve 변경 없음

    def test_add_cash(self):
        r = _reserve()
        r.add_cash(1000, 5)
        self.assertEqual(r.reserve[1000], 5)

    def test_add_cash_accumulates(self):
        r = _reserve({1000: 3})
        r.add_cash(1000, 2)
        self.assertEqual(r.reserve[1000], 5)

    def test_get_total(self):
        r = _reserve({10000: 1, 1000: 2})
        self.assertEqual(r.get_total(), 12000)


class TestCashPayment(unittest.TestCase):

    def test_cash_invalid_amount_negative(self):
        with self.assertRaises(ValueError):
            CashPayment(-1, _reserve())

    def test_cash_invalid_amount_float(self):
        with self.assertRaises(ValueError):
            CashPayment(4000.5, _reserve())

    def test_cash_invalid_amount_bool(self):
        with self.assertRaises(ValueError):
            CashPayment(True, _reserve())

    def test_cash_amount_zero_allowed(self):
        p = CashPayment(0, _reserve())
        self.assertTrue(p.can_complete())

    def test_cash_insert_accumulates(self):
        p = CashPayment(10000, _reserve())
        p.insert(1000)
        p.insert(1000)
        p.insert(5000)
        self.assertEqual(p.inserted_amount, 7000)

    def test_cash_insert_invalid_denomination(self):
        p = CashPayment(5000, _reserve())
        with self.assertRaises(ValueError):
            p.insert(300)

    def test_cash_insert_500_rejected(self):
        p = CashPayment(5000, _reserve())
        with self.assertRaises(ValueError):
            p.insert(500)

    def test_cash_insert_100_rejected(self):
        p = CashPayment(5000, _reserve())
        with self.assertRaises(ValueError):
            p.insert(100)

    def test_cash_insert_zero_rejected(self):
        p = CashPayment(5000, _reserve())
        with self.assertRaises(ValueError):
            p.insert(0)

    def test_cash_can_complete_true(self):
        p = CashPayment(4000, _reserve())
        p.insert(5000)
        self.assertTrue(p.can_complete())

    def test_cash_can_complete_false(self):
        p = CashPayment(4000, _reserve())
        p.insert(1000)
        p.insert(1000)
        p.insert(1000)  # 3000 투입, 4000 미만
        self.assertFalse(p.can_complete())

    def test_cash_can_complete_exact(self):
        p = CashPayment(5000, _reserve())
        p.insert(5000)  # 정확히 5000원 투입
        self.assertTrue(p.can_complete())

    def test_cash_get_change_amount(self):
        p = CashPayment(4000, _reserve())
        p.insert(5000)
        self.assertEqual(p.get_change_amount(), 1000)

    def test_cash_get_change_zero(self):
        p = CashPayment(5000, _reserve())
        p.insert(5000)  # 정확히 5000원 투입 → 잔돈 0
        self.assertEqual(p.get_change_amount(), 0)

    def test_cash_process_success(self):
        # 9000원 결제, 10000원 투입 → 잔돈 1000원
        p = CashPayment(9000, _reserve({1000: 1}))
        p.insert(10000)
        self.assertEqual(p.process(), {1000: 1})

    def test_cash_process_insufficient_change(self):
        p = CashPayment(9000, _reserve())  # 잔돈 없음
        p.insert(10000)
        with self.assertRaises(InsufficientChangeException):
            p.process()


class TestCardPayment(unittest.TestCase):

    def test_card_process_success(self):
        self.assertTrue(CardPayment(4000).process())

    def test_card_process_insufficient(self):
        with self.assertRaises(PaymentException):
            CardPayment(4000, fail_reason="insufficient").process()

    def test_card_process_error(self):
        with self.assertRaises(PaymentException):
            CardPayment(4000, fail_reason="error").process()

    def test_card_invalid_amount_negative(self):
        with self.assertRaises(ValueError):
            CardPayment(-1)

    def test_card_invalid_amount_float(self):
        with self.assertRaises(ValueError):
            CardPayment(4000.5)

    def test_card_invalid_amount_bool(self):
        with self.assertRaises(ValueError):
            CardPayment(True)

    def test_card_amount_zero_allowed(self):
        self.assertTrue(CardPayment(0).process())

    def test_card_invalid_fail_reason(self):
        with self.assertRaises(ValueError):
            CardPayment(4000, fail_reason="xyz")


if __name__ == "__main__":
    unittest.main(verbosity=2)
