class Symptom:
    def __init__(self, symptom_id: str, name: str, is_emergency: bool = False, description: str = ""):
        self.symptom_id = symptom_id
        self.name = name
        self.is_emergency = is_emergency
        self.description = description


class SymptomGroup:
    def __init__(self, symptoms: list | None = None):
        self._index: dict[str, Symptom] = {s.symptom_id: s for s in (symptoms or [])}

    @property
    def symptoms(self) -> list:
        return list(self._index.values())

    def get_symptom(self, symptom_id: str) -> "Symptom | None":
        return self._index.get(symptom_id)

    def get_emergency_symptoms(self) -> list:
        return [s for s in self._index.values() if s.is_emergency]

    def __len__(self) -> int:
        """전체 증상 수 반환"""
        return len(self._index)
