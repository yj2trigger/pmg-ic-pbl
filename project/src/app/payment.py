from app.exceptions import InsufficientChangeException, PaymentException


class ChangeReserve:
    DENOMINATIONS = [50000, 10000, 5000, 1000]

    def __init__(self, reserve: dict):
        self.reserve = reserve  # {50000: n, 10000: n, 5000: n, 1000: n}

    def can_make_change(self, amount: int) -> bool:
        remaining = amount
        for d in self.DENOMINATIONS:
            use = min(remaining // d, self.reserve.get(d, 0))
            remaining -= use * d
        return remaining == 0

    def dispense(self, amount: int) -> dict:
        breakdown = {}
        remaining = amount
        for d in self.DENOMINATIONS:
            use = min(remaining // d, self.reserve.get(d, 0))
            if use > 0:
                breakdown[d] = use
                remaining -= use * d
        if remaining > 0:
            raise InsufficientChangeException("잔돈 부족으로 반환 불가")
        for d, count in breakdown.items():
            self.reserve[d] -= count
        return breakdown

    def add_cash(self, denomination: int, count: int) -> None:
        self.reserve[denomination] = self.reserve.get(denomination, 0) + count

    def get_total(self) -> int:
        return sum(d * count for d, count in self.reserve.items())


class Payment:
    def __init__(self, amount: int):
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
            raise ValueError("결제 금액은 0 이상의 정수여야 합니다")
        self.amount = amount

    def process(self):
        raise NotImplementedError


class CashPayment(Payment):
    def __init__(self, amount: int, change_reserve: ChangeReserve):
        super().__init__(amount)
        self.inserted_amount = 0
        self.change_reserve = change_reserve

    def insert(self, denomination: int) -> None:
        if denomination not in ChangeReserve.DENOMINATIONS:
            raise ValueError(f"유효하지 않은 권종: {denomination}")
        self.inserted_amount += denomination

    def can_complete(self) -> bool:
        return self.inserted_amount >= self.amount

    def get_change_amount(self) -> int:
        return self.inserted_amount - self.amount

    def process(self) -> dict:
        return self.change_reserve.dispense(self.get_change_amount())


class CardPayment(Payment):
    FAIL_REASONS = {"insufficient", "error"}

    def __init__(self, amount: int, fail_reason: str | None = None):
        if fail_reason is not None and fail_reason not in self.FAIL_REASONS:
            raise ValueError(f"예상치 못한 fail_reason: {fail_reason}")
        super().__init__(amount)  # 금액 검증은 Payment.__init__에서 처리
        self.fail_reason = fail_reason

    def process(self) -> bool:
        try:
            if self.fail_reason == "insufficient":
                raise PaymentException("카드 잔액이 부족합니다")
            if self.fail_reason == "error":
                raise PaymentException("카드사의 정기 점검 시간입니다. 잠시 후 다시 시도해주세요.")
            return True
        except PaymentException:
            raise
