# 관리자가 인스턴스 생성
class CustomOption: #옵션의 추가비용 설정
    def __init__(self, option_id: str, name: str, extra_price: int, required_ingredients_dic: dict | None = None):
        self.option_id = option_id
        self.name = name
        self.extra_price = extra_price
        self.required_ingredients_dic = required_ingredients_dic or {}  # {ingredient_id: qty, ...}

    def get_extra_price(self) -> int:
        return self.extra_price


class OptionGroup: #option 옵션 그룹 설정
    def __init__(self, group_id: str, name: str, options: list, active_for: list | None = None):
        # opts = {"size": CustomOption("size_large", "Large", 500)} 같은 상황에서 "size" 자리에 OptionGroup의 name을 넣을 예정
        self.group_id = group_id
        self.name = name
        self.options = options #옵션 리스트
        self.active_for = active_for or [] #설정 안되있으면 모든 상품에서 활성화

    def is_active_for(self, product_type: str) -> bool:
        #해당 상품에서의 활성화 여부 반환
        return not self.active_for or product_type in self.active_for
    

    def get_options(self) -> list:
        # 포함된 옵션들 반환
        return self.options


class Product: # 
    def __init__(self, product_id: str, name: str, base_price: int, is_available: bool, product_type: str):
        self.product_id = product_id
        self.name = name
        self.base_price = base_price
        self.is_available = is_available #판매 가능 여부
        self.product_type = product_type

    def calculate_price(self, selected_options: dict) -> int:
        # 가격 계산
        return self.base_price + sum(
            opt.get_extra_price() for opt in selected_options.values()
        )

    def get_display_name(self) -> str:
        # 상품명 반환
        return self.name


class Coffee(Product):
    def __init__(self, product_id: str, name: str, base_price: int, is_available: bool = True):
        super().__init__(product_id, name, base_price, is_available, "coffee")


class Gummy(Product):
    def __init__(self, product_id: str, name: str, base_price: int, is_available: bool = True):
        super().__init__(product_id, name, base_price, is_available, "gummy")
