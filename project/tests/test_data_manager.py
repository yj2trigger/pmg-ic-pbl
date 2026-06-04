import os
import tempfile

import pytest

from app.data_manager import DataManager
from app.ice_cream import IceCreamProduct
from app.ingredient import Ingredient


@pytest.fixture
def tmp_data_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def dm(tmp_data_dir):
    return DataManager(tmp_data_dir)


class TestLoadSaveProducts:
    def test_load_empty(self, dm):
        assert dm.load_products() == []

    def test_roundtrip(self, dm):
        products = [IceCreamProduct("P-001", "스틱", 3000, True, "stick")]
        dm.save_products(products)
        loaded = dm.load_products()
        assert len(loaded) == 1
        assert loaded[0].product_id == "P-001"
        assert loaded[0].product_type == "stick"

    def test_save_creates_file(self, dm, tmp_data_dir):
        dm.save_products([IceCreamProduct("P-001", "스틱", 3000, True, "stick")])
        assert os.path.exists(os.path.join(tmp_data_dir, "products.json"))

    def test_multiple_products(self, dm):
        products = [
            IceCreamProduct("P-001", "스틱", 3000, True, "stick"),
            IceCreamProduct("P-002", "스쿱", 4000, True, "scoop"),
        ]
        dm.save_products(products)
        loaded = dm.load_products()
        assert len(loaded) == 2
        assert loaded[1].name == "스쿱"

    def test_is_available_preserved(self, dm):
        dm.save_products([IceCreamProduct("P-002", "품절", 1000, False, "scoop")])
        assert dm.load_products()[0].is_available is False

    def test_base_price_preserved(self, dm):
        dm.save_products([IceCreamProduct("P-001", "스틱", 3500, True, "stick")])
        assert dm.load_products()[0].base_price == 3500


class TestLoadSaveIngredients:
    def test_load_empty(self, dm):
        assert dm.load_ingredients() == {}

    def test_roundtrip(self, dm):
        ingredients_list = [
            {"ingredient_id": "mix_vanilla", "name": "바닐라 믹스", "stock": 10, "max_capacity": 50, "unit": "봉"}
        ]
        dm.save_ingredients(ingredients_list)
        loaded = dm.load_ingredients()
        assert "mix_vanilla" in loaded
        assert loaded["mix_vanilla"].name == "바닐라 믹스"

    def test_save_creates_file(self, dm, tmp_data_dir):
        dm.save_ingredients([{"ingredient_id": "i1", "name": "재료", "stock": 5, "max_capacity": 20, "unit": "개"}])
        assert os.path.exists(os.path.join(tmp_data_dir, "ingredients.json"))


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