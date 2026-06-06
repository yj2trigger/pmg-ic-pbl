# ──────────────────────────────────────────────────────────────────────────────
# payment.py — 잔돈 관리(ChangeReserve), 결제 처리(Payment, CashPayment, CardPayment)
#
# [역할]
#   이 파일은 결제와 관련된 세 가지 책임을 담당한다:
#     1. ChangeReserve: 키오스크 내 현금(잔돈용) 보유 관리 + 잔돈 계산
#     2. CashPayment: 현금 투입 누적, 잔돈 처리
#     3. CardPayment: 카드 결제 시뮬레이션
#
# [버그 수정 이력 — 중요]
#   commit 98770e0 에서 현금 투입 버그를 수정했다.
#   버그 내용: CashPayment.process() 에서 잔돈을 계산할 때,
#     투입한 현금이 ChangeReserve에 먼저 추가되어야 잔돈을 뽑을 수 있는데,
#     투입한 지폐의 권종별 카운트(inserted_bills)가 reserve에 반영되지 않는 문제였다.
#   수정 방법: process() 시작 시 inserted_bills를 change_reserve.add_cash()로 먼저 추가.
#   이 버그는 Gemini AI 코드 리뷰가 지적해서 발견했다.
#
# [의존성]
#   import: exceptions.py (InsufficientChangeException, PaymentException)
#   이 파일을 사용하는 곳:
#     main.py → ChangeReserve 인스턴스 생성
#     kiosk_controller.py → start_cash_payment(), process_cash_payment(), 등
#     gui/main_window.py → go_to_cash_payment()에서 CashPayment 직접 생성
#     gui/screens/cash_payment.py → pmt.insert(), pmt.can_complete(), pmt.process()
# ──────────────────────────────────────────────────────────────────────────────

from app.exceptions import InsufficientChangeException, PaymentException


class ChangeReserve:
    # 키오스크 내에 보관된 잔돈용 현금을 관리한다.
    # 결제 완료 시 투입된 현금은 reserve에 추가되고, 잔돈은 reserve에서 차감된다.
    # 데이터는 change_reserve.json에 저장된다. 키오스크 재시작 후에도 잔돈 보유량이 유지된다.

    # DENOMINATIONS: 지원하는 지폐 권종 목록. 내림차순으로 정렬.
    #   잔돈 계산(그리디 알고리즘)에서 큰 권종부터 사용하기 위해 내림차순이다.
    DENOMINATIONS = [50000, 10000, 5000, 1000]

    def __init__(self, reserve: dict):
        # reserve: {지폐액(int): 보유장수(int)} 딕셔너리.
        #   예) {50000: 5, 10000: 10, 5000: 20, 1000: 50}
        #   main.py에서 change_reserve.json을 읽어서 넘겨준다.
        #   JSON 키는 str이므로 main.py에서 {int(k): v} 변환 후 전달된다.
        self.reserve = reserve

    def can_make_change(self, amount: int) -> bool:
        # amount원을 현재 보유한 지폐로 정확히 만들 수 있는지 확인한다.
        # 실제로 차감하지 않고 시뮬레이션만 한다.
        #
        # 알고리즘: 그리디(Greedy) — 큰 권종부터 최대한 사용
        #   1. 50000원짜리를 최대한 사용
        #   2. 남은 금액을 10000원짜리로
        #   3. 계속해서 5000, 1000원 순으로
        #   남은 금액이 0이 되면 잔돈 반환 가능.
        #
        # 왜 그리디를 쓰나?
        #   한국 화폐 단위(1000, 5000, 10000, 50000)는 모두 1000의 배수이므로
        #   그리디 알고리즘이 항상 최적 해(잔돈 최소 지폐 수)를 보장한다.
        remaining = amount
        for d in self.DENOMINATIONS:
            # 이 권종으로 사용할 수 있는 장수: 필요량 대비 보유량 중 작은 값
            use = min(remaining // d, self.reserve.get(d, 0))
            remaining -= use * d
        return remaining == 0

    def dispense(self, amount: int) -> dict:
        # amount원을 보유 현금에서 실제로 꺼낸다 (reserve 차감).
        # 반환값: {권종: 사용장수} 딕셔너리. 영수증 화면에서 잔돈 내역 표시에 사용.
        # 잔돈을 만들 수 없으면 InsufficientChangeException을 raise한다.
        #
        # 왜 can_make_change()를 먼저 호출하지 않고 dispense()에서 직접 처리하나?
        #   두 번 순회하는 것보다 한 번에 시도하고 실패 시 예외를 던지는 게 더 단순하다.
        #   또한 dispense()와 can_make_change() 사이에 reserve가 바뀔 일이 없으므로 안전하다.
        breakdown = {}        # 사용할 권종과 장수를 임시 기록
        remaining = amount

        for d in self.DENOMINATIONS:
            use = min(remaining // d, self.reserve.get(d, 0))
            if use > 0:
                breakdown[d] = use
                remaining -= use * d

        if remaining > 0:
            # 모든 권종을 써도 잔돈을 정확히 만들 수 없는 경우 예외 발생.
            # CashPaymentScreen._complete()이 이 예외를 잡아서 투입금을 환불하고 결제 취소한다.
            raise InsufficientChangeException("잔돈 부족으로 반환 불가")

        # 여기까지 왔다면 잔돈 반환 가능 → reserve에서 실제로 차감
        for d, count in breakdown.items():
            self.reserve[d] -= count

        return breakdown

    def add_cash(self, denomination: int, count: int) -> None:
        # 특정 권종의 지폐를 reserve에 추가한다.
        # 사용처 1: CashPayment.process() — 고객이 투입한 지폐를 reserve에 편입
        # 사용처 2: AdminMenuScreen._add_cash() — 관리자가 수동으로 잔돈 보충
        # denomination 검증: CashPayment.insert()와 동일한 DENOMINATIONS 기준 사용
        if denomination not in self.DENOMINATIONS:
            raise ValueError(f"유효하지 않은 권종: {denomination}")
        # count 검증: Payment.__init__과 동일한 패턴 (bool은 int 하위 타입이므로 명시 제외)
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            raise ValueError(f"count는 양의 정수여야 합니다: {count}")
        self.reserve[denomination] = self.reserve.get(denomination, 0) + count

    def get_total(self) -> int:
        # 현재 reserve에 있는 현금 총액(원)을 반환한다.
        # AdminMenuScreen._show_cash()에서 "현금 보유량: n원" 표시에 사용.
        return sum(d * count for d, count in self.reserve.items())


class Payment:
    # CashPayment, CardPayment의 공통 부모 클래스.
    # amount 유효성 검증을 한 곳에서 처리하기 위해 분리했다.
    # 직접 인스턴스화하지 않는다 — 하위 클래스를 사용한다.

    def __init__(self, amount: int):
        # amount 유효성 검증: 정수이고 0 이상이어야 한다.
        # isinstance(amount, bool) 추가 이유: Python에서 bool은 int의 하위 타입이므로
        #   True(1), False(0)도 int 검사를 통과한다. 명시적으로 제외한다.
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
            raise ValueError("결제 금액은 0 이상의 정수여야 합니다")
        self.amount = amount

    def process(self):
        # 하위 클래스에서 반드시 구현해야 한다.
        # 구현하지 않으면 NotImplementedError가 발생한다.
        raise NotImplementedError


class CashPayment(Payment):
    # 현금 결제를 처리한다.
    # 사용자가 지폐를 한 장씩 투입하고, 투입 총액이 결제 금액 이상이 되면 완료 가능해진다.
    # 잔돈은 process() 시점에 ChangeReserve에서 계산 및 반환된다.

    def __init__(self, amount: int, change_reserve: ChangeReserve):
        super().__init__(amount)     # 금액 유효성 검증은 Payment.__init__에서 처리
        self.inserted_amount = 0    # 지금까지 투입된 총액
        # inserted_bills: {권종: 투입장수}. 버그 수정(98770e0) 이후 추가된 필드.
        #   process() 시 투입한 지폐를 reserve에 더하기 위해 권종별로 기록한다.
        self.inserted_bills: dict[int, int] = {}
        self.change_reserve = change_reserve

    def insert(self, denomination: int) -> None:
        # 지폐 1장을 투입한다.
        # denomination이 DENOMINATIONS에 없으면 ValueError 발생.
        if denomination not in ChangeReserve.DENOMINATIONS:
            raise ValueError(f"유효하지 않은 권종: {denomination}")
        self.inserted_amount += denomination
        # 권종별 투입 장수 누적 (process()에서 reserve에 추가할 때 사용)
        self.inserted_bills[denomination] = self.inserted_bills.get(denomination, 0) + 1

    def can_complete(self) -> bool:
        # 투입 금액이 결제 금액 이상인지 확인한다.
        # CashPaymentScreen._update_status()에서 "결제 완료" 버튼 활성화 여부를 결정한다.
        # 잔돈 가능 여부(can_make_change)는 여기서 확인하지 않는다.
        # 이유: 실제 키오스크에서 사용자가 이미 돈을 투입 중인 상황에서
        #   물리적으로 투입을 막는 것은 불가능하다. 잔돈 부족은 process() 시점에
        #   InsufficientChangeException으로 처리하고 투입금을 환불한다.
        return self.inserted_amount >= self.amount

    def get_change_amount(self) -> int:
        # 반환할 잔돈 금액을 계산한다.
        # inserted_amount - amount. 결제 금액을 초과해서 넣은 경우 양수가 된다.
        return self.inserted_amount - self.amount

    def process(self) -> dict:
        # 결제를 완료하고 잔돈을 반환한다.
        # 반환값: {권종: 반환장수} 딕셔너리. 영수증에 잔돈 내역으로 표시된다.
        #
        # [핵심 로직 — 버그 수정 포인트]
        # 1단계: 투입한 지폐를 먼저 reserve에 추가한다.
        #   이유: 잔돈을 계산하려면 투입된 현금도 reserve에 있어야 한다.
        #   예) 투입 10000원, 결제 3000원, 잔돈 7000원
        #       → reserve에 10000원을 추가한 뒤 7000원을 꺼내야 한다.
        #   버그(98770e0 이전): inserted_bills를 reserve에 추가하지 않아서
        #     잔돈 계산 시 투입금이 반영되지 않았다.
        for denom, count in self.inserted_bills.items():
            self.change_reserve.add_cash(denom, count)

        # 2단계: 잔돈을 reserve에서 꺼낸다.
        #   get_change_amount() = 0이면 딕셔너리 빈 값({}) 반환 (잔돈 없음).
        result = self.change_reserve.dispense(self.get_change_amount())
        # 이중 호출 방지: process() 후 inserted_bills 초기화.
        # 같은 객체로 재호출 시 투입금이 reserve에 이중으로 더해지는 것을 막는다.
        self.inserted_bills = {}
        return result


class CardPayment(Payment):
    # 카드 결제를 시뮬레이션한다.
    # 실제 카드 API 연동은 없고, fail_reason 파라미터로 실패 케이스를 재현할 수 있다.
    # 이 파라미터는 테스트 및 데모에서만 사용하고, 실제 사용자 흐름에서는 None으로 호출된다.

    FAIL_REASONS = {"insufficient", "error"}
    # insufficient: 카드 잔액 부족
    # error: 카드사 시스템 오류

    def __init__(self, amount: int, fail_reason: str | None = None):
        # fail_reason 유효성 검증: None이거나 FAIL_REASONS 안의 값이어야 한다.
        if fail_reason is not None and fail_reason not in self.FAIL_REASONS:
            raise ValueError(f"예상치 못한 fail_reason: {fail_reason}")
        super().__init__(amount)     # 금액 검증은 Payment.__init__에서 처리
        self.fail_reason = fail_reason

    def process(self) -> bool:
        # 카드 결제를 처리한다.
        # 성공 시 True 반환. 실패 시 PaymentException raise.
        # main_window.go_to_card_payment()가 try/except로 이 메서드를 호출한다.
        try:
            if self.fail_reason == "insufficient":
                raise PaymentException("카드 잔액이 부족합니다")
            if self.fail_reason == "error":
                raise PaymentException("카드사의 정기 점검 시간입니다. 잠시 후 다시 시도해주세요.")
            return True
        except PaymentException:
            # PaymentException은 잡지 않고 다시 던져서 호출자가 처리하게 한다.
            # (except가 있는 이유: 향후 로그 기록 등 추가 처리를 위한 자리)
            raise
