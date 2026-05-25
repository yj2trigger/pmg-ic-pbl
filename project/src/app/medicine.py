class Medicine:
    def __init__(
        self,
        medicine_id: str,
        name: str,
        base_price: int,
        is_available: bool,
        symptom_categories: list[str],
        description: str = "",
        dosage: str = "",
        caution: str = "",
    ):
        self.medicine_id = medicine_id
        self.name = name
        self.base_price = base_price
        self.is_available = is_available
        self.symptom_categories: list[str] = symptom_categories
        self.description = description
        self.dosage = dosage
        self.caution = caution

    def calculate_price(self) -> int:
        return self.base_price

    def get_display_name(self) -> str:
        return self.name
