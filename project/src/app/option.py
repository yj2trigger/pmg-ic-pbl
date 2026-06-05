# ──────────────────────────────────────────────────────────────────────────────
# option.py — 옵션(Option)과 옵션 그룹(OptionGroup) 도메인 클래스
#
# [역할]
#   Option: 선택 가능한 단일 옵션. 추가 금액과 필요 재료 정보를 가진다.
#   OptionGroup: 같은 카테고리의 옵션 묶음 (예: "코팅 선택").
#     is_active_for()로 상품 타입에 맞는 그룹만 필터링한다.
#
# [데이터 흐름]
#   options.json → DataManager.load_option_groups() → OptionGroup(**item)
#     → OptionGroup.__init__에서 options 리스트를 [Option(**o) for o in options] 변환
#
# [의존성]
#   이 파일을 사용하는 곳:
#     data_manager.py → load_option_groups()
#     kiosk_controller.py → get_option_groups(), get_unavailable_options()
#     gui/screens/customize.py → OptionGroupWidget(group, ...)
# ──────────────────────────────────────────────────────────────────────────────

class Option:
    def __init__(self, option_id: str, name: str, extra_price: int,
                 required_ingredients_dic: dict):
        self.option_id = option_id
        self.name = name
        self.extra_price = extra_price
        self.required_ingredients_dic = required_ingredients_dic


class OptionGroup:
    def __init__(self, group_id: str, name: str, active_for: list, options: list):
        self.group_id = group_id
        self.name = name
        self._active_for = active_for
        self._options = [Option(**o) for o in options]

    def is_active_for(self, product_type: str) -> bool:
        return product_type in self._active_for

    def get_options(self) -> list["Option"]:
        return self._options
