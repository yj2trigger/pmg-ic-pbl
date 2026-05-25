import unittest
from app.medicine import Medicine
from app.symptom import Symptom, SymptomGroup


class TestMedicine(unittest.TestCase):

    def setUp(self):
        self.medicine = Medicine(
            medicine_id="tylenol_500",
            name="타이레놀 500mg",
            base_price=3500,
            is_available=True,
            symptom_categories=["headache", "cold"],
            description="해열 및 진통 효과",
            dosage="1회 1정, 1일 3회",
            caution="공복 복용 주의",
        )

    def test_medicine_create(self):
        self.assertEqual(self.medicine.medicine_id, "tylenol_500")
        self.assertEqual(self.medicine.name, "타이레놀 500mg")
        self.assertEqual(self.medicine.base_price, 3500)
        self.assertEqual(self.medicine.description, "해열 및 진통 효과")
        self.assertEqual(self.medicine.dosage, "1회 1정, 1일 3회")
        self.assertEqual(self.medicine.caution, "공복 복용 주의")

    def test_symptom_categories_multi(self):
        self.assertIn("headache", self.medicine.symptom_categories)
        self.assertIn("cold", self.medicine.symptom_categories)
        self.assertEqual(len(self.medicine.symptom_categories), 2)

    def test_medicine_available(self):
        self.assertTrue(self.medicine.is_available)

    def test_medicine_unavailable(self):
        m = Medicine("x", "없는약", 1000, False, ["headache"])
        self.assertFalse(m.is_available)

    def test_medicine_price(self):
        self.assertEqual(self.medicine.calculate_price(), 3500)
        self.assertEqual(self.medicine.calculate_price({}), 3500)

    def test_medicine_display_name(self):
        self.assertEqual(self.medicine.get_display_name(), "타이레놀 500mg")


class TestSymptom(unittest.TestCase):

    def test_symptom_create(self):
        s = Symptom("headache", "두통 / 열", is_emergency=False, description="두통, 발열 증상")
        self.assertEqual(s.symptom_id, "headache")
        self.assertEqual(s.name, "두통 / 열")
        self.assertFalse(s.is_emergency)

    def test_symptom_emergency(self):
        s = Symptom("chest_pain", "흉통", is_emergency=True)
        self.assertTrue(s.is_emergency)

    def test_symptom_group_get(self):
        s1 = Symptom("headache", "두통 / 열")
        s2 = Symptom("cold", "감기")
        group = SymptomGroup([s1, s2])
        self.assertIs(group.get_symptom("headache"), s1)
        self.assertIsNone(group.get_symptom("unknown"))

    def test_symptom_group_emergency(self):
        s1 = Symptom("headache", "두통 / 열", is_emergency=False)
        s2 = Symptom("chest_pain", "흉통", is_emergency=True)
        group = SymptomGroup([s1, s2])
        emergency = group.get_emergency_symptoms()
        self.assertEqual(len(emergency), 1)
        self.assertEqual(emergency[0].symptom_id, "chest_pain")


if __name__ == "__main__":
    unittest.main()
