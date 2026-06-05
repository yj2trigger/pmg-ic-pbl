# ──────────────────────────────────────────────────────────────────────────────
# exceptions.py — 프로젝트 전용 예외 계층 정의
#
# [역할]
#   모든 도메인 예외는 KioskException을 공통 루트로 상속한다.
#   try/except KioskException 으로 비즈니스 오류를 한 번에 처리할 수 있다.
#
# [예외 목록]
#   StockOverflowException    — replenish() 시 max_capacity 초과
#   InsufficientStockException — deduct() 또는 add_item() 시 재고 부족
#   InsufficientChangeException — dispense() 시 잔돈 부족
#   PaymentException          — 카드 결제 시뮬레이션 실패
#   AdminAuthException        — 관리자 비밀번호 불일치
#   InvalidRecipeException    — 옵션 설정 오류 (현재 미사용)
#
# [의존성]
#   이 파일을 사용하는 곳: ingredient.py, cart.py, payment.py,
#                         kiosk_controller.py, gui/screens/cash_payment.py
# ──────────────────────────────────────────────────────────────────────────────

class KioskException(Exception):
    pass


class StockOverflowException(KioskException):
    pass


class InsufficientStockException(KioskException):
    pass


class InsufficientChangeException(KioskException):
    pass


class PaymentException(KioskException):
    pass


class AdminAuthException(KioskException):
    pass


class InvalidRecipeException(KioskException):
    pass
