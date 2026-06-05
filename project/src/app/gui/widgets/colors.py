# ──────────────────────────────────────────────────────────────────────────────
# colors.py — 아이스크림 프리뷰 위젯 공유 색상 상수
# [역할]  맛 이름 → QColor 매핑 딕셔너리 단일 정의. 색상 수정은 이 파일 한 곳만.
# [의존성]
#   import  : PyQt6.QtGui.QColor
#   사용하는 곳 : stick_preview.py, scoop_preview.py → FLAVOR_COLORS[key] 로 참조
# ──────────────────────────────────────────────────────────────────────────────
from PyQt6.QtGui import QColor

# 맛 이름(소문자 영문 키) → 아이스크림 본체 색상
FLAVOR_COLORS: dict[str, QColor] = {
    "vanilla":    QColor(255, 243, 176),
    "choco":      QColor(101,  67,  33),
    "strawberry": QColor(252, 129, 145),
    "mint":       QColor(152, 225, 183),
    "mango":      QColor(255, 179,  71),
}
