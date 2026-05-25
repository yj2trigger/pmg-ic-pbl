"""관리자 현금 보유량 표시 테스트"""
import io
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from app.cart import Cart
from app.cli_view import CLIView
from app.data_manager import DataManager
from app.drug_controller import DrugController
from app.payment import ChangeReserve


def _make_cli() -> CLIView:
    dm = MagicMock(spec=DataManager)
    dm.load_admin_config.return_value = {"password": "1234"}
    dm.load_medicines.return_value = []
    dm.load_symptoms.return_value = MagicMock()
    ctrl = DrugController(dm)
    cart = Cart()
    reserve = ChangeReserve({50000: 5, 10000: 10, 5000: 20, 1000: 50})
    return CLIView(ctrl, cart, reserve)


class TestAdminCashDisplay(unittest.TestCase):

    def _run_with_inputs(self, inputs: list) -> str:
        cli = _make_cli()
        buf = io.StringIO()
        with patch("builtins.input", side_effect=inputs), \
             patch("sys.stdout", new=buf):
            try:
                cli._show_admin_menu({"password": "1234"})
            except (StopIteration, EOFError):
                pass
        return buf.getvalue()

    def test_shows_denomination_breakdown(self):
        output = self._run_with_inputs(["3", "0"])
        for denom in ["50,000원", "10,000원", "5,000원", "1,000원"]:
            self.assertIn(denom, output, f"권종 '{denom}' 표시 없음")

    def test_shows_count_with_unit(self):
        output = self._run_with_inputs(["3", "0"])
        self.assertIn("장", output, "개수 단위 '장'이 표시되지 않음")

    def test_total_still_present(self):
        output = self._run_with_inputs(["3", "0"])
        self.assertIn("현금 보유량", output)

    def test_denomination_counts_correct(self):
        output = self._run_with_inputs(["3", "0"])
        self.assertIn("5장", output)   # 50,000원권: 5장
        self.assertIn("10장", output)  # 10,000원권: 10장


if __name__ == "__main__":
    unittest.main(verbosity=2)
