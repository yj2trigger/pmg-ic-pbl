from app.data_manager import DataManager
from app.medicine import Medicine
from app.symptom import SymptomGroup


class DrugController:
    def __init__(self, data_manager: DataManager):
        self._dm = data_manager

    def get_all_symptoms(self) -> SymptomGroup:
        return self._dm.load_symptoms()

    def get_medicines_for_symptom(self, symptom_name: str) -> list[Medicine]:
        return [
            m for m in self._dm.load_medicines()
            if symptom_name in m.symptom_categories and m.is_available
        ]

    def get_available_medicines(self) -> list[Medicine]:
        return [m for m in self._dm.load_medicines() if m.is_available]

    def get_medicine_by_id(self, medicine_id: str) -> "Medicine | None":
        for m in self._dm.load_medicines():
            if m.medicine_id == medicine_id:
                return m
        return None
