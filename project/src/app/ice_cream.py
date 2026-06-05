# ──────────────────────────────────────────────────────────────────────────────
# ice_cream.py — 아이스크림 상품 도메인 클래스
#
# [역할]
#   IceCreamProduct: 상품 ID·이름·기본 가격·판매 여부·상품 타입을 보관한다.
#   calculate_price()로 옵션 추가 금액을 합산한 최종 가격을 반환한다.
#
# [상품 타입]
#   "stick" — 스틱 아이스크림 (모양/코팅/토핑 옵션)
#   "scoop" — 스쿱 아이스크림 (용기/맛 1~3 옵션)
#   product_type은 OptionGroup.is_active_for()에서 활성 옵션 그룹 필터링에 사용된다.
#
# [의존성]
#   이 파일을 사용하는 곳:
#     data_manager.py → load_products()에서 IceCreamProduct(**item) 생성
#     kiosk_controller.py → get_available_products(), add_to_cart() 등
#     gui/screens/main_menu.py → 상품 버튼 렌더링
# ──────────────────────────────────────────────────────────────────────────────

class IceCreamProduct:
    def __init__(self, product_id: str, name: str, base_price: int,
                 is_available: bool, product_type: str):
        self.product_id = product_id
        self.name = name
        self.base_price = base_price
        self.is_available = is_available
        self.product_type = product_type

    def calculate_price(self, selected_options=None) -> int:
        price = self.base_price
        if selected_options:
            for opt in selected_options.values():
                if opt and hasattr(opt, "extra_price"):
                    price += opt.extra_price
        return price

    def get_display_name(self) -> str:
        return self.name
