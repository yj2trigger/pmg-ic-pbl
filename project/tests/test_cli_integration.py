"""
CLI subprocess 통합 테스트 — 자가 진단 도구

GUI 없이 subprocess 수준에서 CLI 동작을 직접 검증한다.
"GUI가 X를 보내면 CLI는 Y를 반환해야 한다" 형태로 테스트한다.

실행: PYTHONPATH=src python -m unittest tests.test_cli_integration -v
"""
import unittest
import subprocess
import sys
import os
import time

_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project/
MAIN  = os.path.join(_DIR, 'src', 'app', 'main.py')


def _run(inputs: list[str], timeout: float = 3.0) -> str:
    """
    main.py 를 subprocess 로 실행하고, inputs 순서대로 stdin에 전송한 뒤
    수집된 stdout 전체를 반환한다.
    """
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

    # 각 입력 사이에 짧은 지연을 두어 CLI가 처리할 시간을 줌
    stdin_data = ''
    for inp in inputs:
        stdin_data += inp + '\n'

    try:
        out, _ = proc.communicate(input=stdin_data, timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()

    return out


class TestAdminPasswordDiagnosis(unittest.TestCase):
    """
    관리자 비밀번호 현황을 진단한다.
    테스트 결과로 어떤 패스워드가 실제 저장되어 있는지 알 수 있다.
    """

    def _try_admin(self, password: str) -> str:
        """idle 화면 → 메인 메뉴 → 관리자(4) → password 입력 → 결과 반환"""
        return _run([
            '\n',        # idle → main menu
            '4',         # 관리자 선택
            password,    # 패스워드 입력
            '0',         # 관리자 메뉴 종료 (성공 시)
            '0',         # 처음 화면
        ], timeout=5.0)

    def test_DIAG01_stored_password_is_1234(self):
        """저장된 관리자 패스워드가 '1234'여야 한다."""
        out = self._try_admin('1234')
        self.assertIn('관리자 메뉴', out,
                      f"패스워드 '1234'로 관리자 메뉴 진입 실패.\n"
                      f"실제 출력:\n{out[-300:]}")
        self.assertNotIn('인증 실패', out)

    def test_DIAG02_wrong_password_rejected(self):
        """잘못된 패스워드('0')는 거부되어야 한다."""
        out = self._try_admin('0')
        self.assertIn('인증 실패', out,
                      f"패스워드 '0'이 거부되지 않았다 — 저장된 패스워드가 '0'일 수 있음.\n"
                      f"실제 출력:\n{out[-300:]}")
        self.assertNotIn('관리자 메뉴', out)

    def test_DIAG03_admin_menu_shows_all_options(self):
        """관리자 메뉴에 6개 항목(재고보충~키오스크 종료)이 모두 표시되어야 한다."""
        out = self._try_admin('1234')
        for label in ['재고 보충', '상품 ON/OFF', '가격 변경',
                      '현금 보유량', '비밀번호 변경', '키오스크 종료']:
            self.assertIn(label, out,
                          f"관리자 메뉴에 '{label}'이 표시되지 않음")


class TestCliSendReceive(unittest.TestCase):
    """
    GUI가 특정 값을 전송했을 때 CLI가 올바르게 반응하는지 검증한다.
    """

    def test_DIAG04_main_menu_appears_after_start(self):
        """idle 화면 터치 후 주문 메뉴가 표시되어야 한다."""
        out = _run(['\n', '0'], timeout=4.0)
        self.assertIn('주문 메뉴', out)

    def test_DIAG05_coffee_flow_shows_options(self):
        """커피(1) 선택 후 커피 선택 화면이 표시되어야 한다."""
        out = _run(['\n', '1', '0'], timeout=4.0)
        self.assertIn('커피 선택', out)

    def test_DIAG06_admin_config_file_has_correct_password(self):
        """admin_config.json 의 실제 패스워드를 직접 확인한다."""
        import json, os
        data_dir = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'app', 'data'
        )
        cfg_path = os.path.join(data_dir, 'admin_config.json')

        if not os.path.exists(cfg_path):
            self.skipTest('admin_config.json 미존재 — 첫 실행 후 재시도')

        with open(cfg_path, encoding='utf-8') as f:
            cfg = json.load(f)

        self.assertEqual(cfg.get('password'), '1234',
                         f"admin_config.json 의 패스워드가 '1234'가 아님: {cfg}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
