import pytest
from unittest.mock import MagicMock

from app.drug_controller import DrugController
from app.medicine import Medicine
from app.symptom import Symptom, SymptomGroup


@pytest.fixture
def medicines():
    return [
        Medicine("MED-001", "타이레놀", 5500, True, ["두통", "발열"]),
        Medicine("MED-002", "판콜에이", 4000, True, ["감기", "두통"]),
        Medicine("MED-003", "품절약", 3000, False, ["두통"]),
    ]


@pytest.fixture
def symptom_group():
    return SymptomGroup([
        Symptom("SYM-001", "두통"),
        Symptom("SYM-002", "흉통", is_emergency=True),
    ])


@pytest.fixture
def dm(medicines, symptom_group):
    mock = MagicMock()
    mock.load_medicines.return_value = medicines
    mock.load_symptoms.return_value = symptom_group
    return mock


@pytest.fixture
def ctrl(dm):
    return DrugController(dm)


class TestGetMedicinesForSymptom:
    def test_returns_matching_available(self, ctrl):
        result = ctrl.get_medicines_for_symptom("두통")
        assert len(result) == 2
        assert all("두통" in m.symptom_categories for m in result)

    def test_excludes_unavailable(self, ctrl):
        result = ctrl.get_medicines_for_symptom("두통")
        assert all(m.is_available for m in result)

    def test_no_match_returns_empty(self, ctrl):
        assert ctrl.get_medicines_for_symptom("없는증상") == []

    def test_single_match(self, ctrl):
        result = ctrl.get_medicines_for_symptom("감기")
        assert len(result) == 1
        assert result[0].medicine_id == "MED-002"


class TestGetAvailableMedicines:
    def test_excludes_unavailable(self, ctrl):
        result = ctrl.get_available_medicines()
        assert all(m.is_available for m in result)
        assert len(result) == 2

    def test_returns_medicine_instances(self, ctrl):
        assert all(isinstance(m, Medicine) for m in ctrl.get_available_medicines())


class TestGetMedicineById:
    def test_found(self, ctrl):
        m = ctrl.get_medicine_by_id("MED-001")
        assert m.name == "타이레놀"

    def test_not_found(self, ctrl):
        assert ctrl.get_medicine_by_id("MED-999") is None


class TestGetAllSymptoms:
    def test_returns_symptom_group(self, ctrl):
        assert isinstance(ctrl.get_all_symptoms(), SymptomGroup)

    def test_emergency_symptom_accessible(self, ctrl):
        group = ctrl.get_all_symptoms()
        emergency = group.get_emergency_symptoms()
        assert len(emergency) == 1
        assert emergency[0].symptom_id == "SYM-002"
