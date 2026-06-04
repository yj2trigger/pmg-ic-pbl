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
