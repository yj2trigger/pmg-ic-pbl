"""
관리자 현금 보유량 표시 테스트

현재(수정 전): 총 액수만 표시
목표(수정 후): 권종별 개수까지 표시
"""
import unittest
import subprocess
import sys
import os

_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN  = os.path.join(_DIR, 'src', 'app', 'main.py')


def _run_to_cash_menu() -> str:
    """idle → 메인메뉴 → 관리자(4) → 비밀번호(1234) → 현금보유량(4) → 종료(0) → 처음(0)"""
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    proc = subprocess.Popen(
        [sys.executable, '-u', MAIN],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8',
        errors='replace',
        env=env,
        cwd=os.path.join(_DIR, 'src', 'app'),
    )
    stdin_data = '\n'.join(['', '4', '1234', '4', '0', '0']) + '\n'
    try:
        out, _ = proc.communicate(input=stdin_data, timeout=6.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()
    return out


class TestAdminCashDisplay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.output = _run_to_cash_menu()

    # ── 회귀 테스트 ────────────────────────────────────────────
    def test_AFTER_shows_denomination_breakdown(self):
        """[목표] 각 권종별 보유 개수가 표시된다."""
        for denom in ['50,000원', '10,000원', '5,000원', '1,000원']:
            self.assertIn(denom, self.output,
                          f"권종 '{denom}' 표시 없음")

    def test_AFTER_shows_count_with_unit(self):
        """[목표] 개수가 '장' 단위로 표시된다."""
        self.assertIn('장', self.output,
                      "개수 단위 '장'이 표시되지 않음")

    def test_AFTER_total_still_present(self):
        """[목표] 총액도 함께 표시된다."""
        self.assertIn('현금 보유량', self.output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
