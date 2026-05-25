import os
import tempfile

import pytest

from app.data_manager import DataManager
from app.medicine import Medicine
from app.symptom import Symptom, SymptomGroup


@pytest.fixture
def tmp_data_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def dm(tmp_data_dir):
    return DataManager(tmp_data_dir)


class TestLoadSaveMedicines:
    def test_load_empty(self, dm):
        assert dm.load_medicines() == []

    def test_roundtrip(self, dm):
        medicines = [
            Medicine("MED-001", "타이레놀", 5500, True, ["두통", "발열"], "설명", "1일 3회", "주의")
        ]
        dm.save_medicines(medicines)
        loaded = dm.load_medicines()
        assert len(loaded) == 1
        assert loaded[0].medicine_id == "MED-001"
        assert loaded[0].symptom_categories == ["두통", "발열"]

    def test_save_creates_file(self, dm, tmp_data_dir):
        dm.save_medicines([Medicine("MED-001", "타이레놀", 5500, True, [])])
        assert os.path.exists(os.path.join(tmp_data_dir, "medicines.json"))

    def test_multiple_medicines(self, dm):
        medicines = [
            Medicine("MED-001", "타이레놀", 5500, True, ["두통"]),
            Medicine("MED-002", "판콜", 4000, True, ["감기"]),
        ]
        dm.save_medicines(medicines)
        loaded = dm.load_medicines()
        assert len(loaded) == 2
        assert loaded[1].name == "판콜"

    def test_is_available_preserved(self, dm):
        medicines = [Medicine("MED-001", "품절약", 1000, False, [])]
        dm.save_medicines(medicines)
        assert dm.load_medicines()[0].is_available is False


class TestLoadSaveSymptoms:
    def test_load_empty_returns_symptom_group(self, dm):
        group = dm.load_symptoms()
        assert isinstance(group, SymptomGroup)
        assert group.symptoms == []

    def test_roundtrip(self, dm):
        group = SymptomGroup([
            Symptom("SYM-001", "두통", False, "머리 통증"),
            Symptom("SYM-002", "흉통", True, "응급"),
        ])
        dm.save_symptoms(group)
        loaded = dm.load_symptoms()
        assert loaded.get_symptom("SYM-001").name == "두통"
        assert loaded.get_symptom("SYM-002").is_emergency is True

    def test_emergency_preserved(self, dm):
        group = SymptomGroup([Symptom("SYM-001", "흉통", True)])
        dm.save_symptoms(group)
        loaded = dm.load_symptoms()
        assert loaded.get_emergency_symptoms()[0].symptom_id == "SYM-001"

    def test_nonexistent_symptom_returns_none(self, dm):
        group = SymptomGroup([Symptom("SYM-001", "두통")])
        dm.save_symptoms(group)
        loaded = dm.load_symptoms()
        assert loaded.get_symptom("SYM-999") is None

    def test_symptom_group_lookup_by_id(self, dm):
        group = SymptomGroup([
            Symptom("SYM-001", "두통"),
            Symptom("SYM-002", "발열"),
        ])
        dm.save_symptoms(group)
        loaded = dm.load_symptoms()
        assert loaded.get_symptom("SYM-002").name == "발열"


class TestAdminAndChangeReserve:
    def test_change_reserve_default(self, dm):
        assert dm.load_change_reserve() == {}

    def test_admin_config_default(self, dm):
        assert dm.load_admin_config() == {}

    def test_change_reserve_roundtrip(self, dm):
        dm.save_change_reserve({"500": 3})
        assert dm.load_change_reserve() == {"500": 3}

    def test_admin_config_roundtrip(self, dm):
        dm.save_admin_config({"admin_password": "1234"})
        assert dm.load_admin_config() == {"admin_password": "1234"}
