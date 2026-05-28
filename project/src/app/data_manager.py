import json
import os

from app.medicine import Medicine
from app.symptom import Symptom, SymptomGroup


class DataManager:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def _path(self, filename: str) -> str:
        return os.path.join(self.data_dir, filename)

    def _load(self, filename: str, default):
        path = self._path(filename)
        if not os.path.exists(path):
            return default
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, filename: str, data) -> None:
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self._path(filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_medicines(self) -> list[Medicine]:
        raw = self._load("medicines.json", [])
        return [Medicine(**item) for item in raw]

    def save_medicines(self, medicines: list[Medicine]) -> None:
        data = [
            {
                "medicine_id": m.medicine_id,
                "name": m.name,
                "base_price": m.base_price,
                "is_available": m.is_available,
                "symptom_categories": m.symptom_categories,
                "description": m.description,
                "dosage": m.dosage,
                "caution": m.caution,
            }
            for m in medicines
        ]
        self._save("medicines.json", data)

    def load_symptoms(self) -> SymptomGroup:
        raw = self._load("symptoms.json", [])
        symptoms = [Symptom(**item) for item in raw]
        return SymptomGroup(symptoms)

    def save_symptoms(self, group: SymptomGroup) -> None:
        data = [
            {
                "symptom_id": s.symptom_id,
                "name": s.name,
                "is_emergency": s.is_emergency,
                "description": s.description,
            }
            for s in group.symptoms
        ]
        self._save("symptoms.json", data)

    def load_change_reserve(self) -> dict:
        return self._load("change_reserve.json", {})

    def save_change_reserve(self, data: dict) -> None:
        self._save("change_reserve.json", data)

    def load_admin_config(self) -> dict:
        return self._load("admin_config.json", {})

    def save_admin_config(self, data: dict) -> None:
        self._save("admin_config.json", data)
