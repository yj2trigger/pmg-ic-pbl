import unittest
import tempfile
import os

from app.data_manager import DataManager
from app.exceptions import InvalidRecipeException


class TestDataManager(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.dm = DataManager(self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_save_load_products(self):
        data = [{"product_id": "p1", "name": "아메리카노", "base_price": 3000}]
        self.dm.save_products(data)
        self.assertEqual(self.dm.load_products(), data)

    def test_save_load_ingredients(self):
        data = [{"ingredient_id": "i1", "name": "원두", "stock": 50}]
        self.dm.save_ingredients(data)
        self.assertEqual(self.dm.load_ingredients(), data)

    def test_save_load_change_reserve(self):
        data = {10000: 2, 5000: 3, 1000: 5}
        self.dm.save_change_reserve(data)
        loaded = self.dm.load_change_reserve()
        # JSON 키는 문자열로 역직렬화됨
        self.assertEqual(loaded["10000"], 2)
        self.assertEqual(loaded["5000"], 3)

    def test_save_load_admin_config(self):
        data = {"password": "1234", "top_n": 3}
        self.dm.save_admin_config(data)
        self.assertEqual(self.dm.load_admin_config(), data)

    def test_invalid_recipe_json(self):
        import json
        path = os.path.join(self.tmp, "recipes.json")
        with open(path, "w") as f:
            json.dump([1, 2, 3], f)  # dict가 아닌 list
        with self.assertRaises(InvalidRecipeException):
            self.dm.load_recipes()

    def test_missing_file_returns_default(self):
        self.assertEqual(self.dm.load_products(), [])
        self.assertEqual(self.dm.load_ingredients(), [])
        self.assertEqual(self.dm.load_recipes(), {})
        self.assertEqual(self.dm.load_options(), [])
        self.assertEqual(self.dm.load_change_reserve(), {})
        self.assertEqual(self.dm.load_admin_config(), {})

    def test_save_load_options(self):
        data = [{"group_id": "size", "name": "크기"}]
        self.dm.save_options(data)
        self.assertEqual(self.dm.load_options(), data)

    def test_save_load_recipes(self):
        data = {"coffee": {"size_large": {"coffee_bean": 2}}}
        self.dm.save_recipes(data)
        self.assertEqual(self.dm.load_recipes(), data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
