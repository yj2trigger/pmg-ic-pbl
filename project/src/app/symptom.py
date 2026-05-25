class Symptom:
    def __init__(self, symptom_id: str, name: str, is_emergency: bool = False, description: str = ""):
        self.symptom_id = symptom_id
        self.name = name
        self.is_emergency = is_emergency
        self.description = description


class SymptomGroup:
    def __init__(self, symptoms: list | None = None):
        self.symptoms: list[Symptom] = symptoms or []

    def get_symptom(self, symptom_id: str) -> "Symptom | None":
        for s in self.symptoms:
            if s.symptom_id == symptom_id:
                return s
        return None

    def get_emergency_symptoms(self) -> list:
        return [s for s in self.symptoms if s.is_emergency]
