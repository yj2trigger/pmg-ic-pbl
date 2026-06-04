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
