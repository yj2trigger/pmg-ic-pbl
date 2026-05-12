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
