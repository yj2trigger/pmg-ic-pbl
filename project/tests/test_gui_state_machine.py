import unittest

from app.gui.state_machine import GUIStateMachine, ScreenState

SEP = '─' * 40


def _screen(header_line: str, *option_lines, prompt: str = '선택: ') -> str:
    """테스트용 CLI 화면 텍스트 조합 헬퍼."""
    body = '\n'.join(option_lines)
    return f'{SEP}\n{header_line}\n{body}\n{prompt}'


class TestFeedReturnsNone(unittest.TestCase):

    def test_TC_G02_01_no_prompt_returns_none(self):
        """프롬프트 없는 텍스트 → None 반환."""
        sm = GUIStateMachine()
        result = sm.feed("안녕\n")
        self.assertIsNone(result)


class TestMainMenuDetection(unittest.TestCase):

    def setUp(self):
        self.sm = GUIStateMachine()

    def _feed_main_menu(self):
        text = _screen(
            '[ 주문 메뉴 ]',
            '  1. 커피 주문',
            '  2. 구미 주문',
            '  3. 수량 변경',
            '  4. 관리자',
            '  0. 처음 화면',
        )
        return self.sm.feed(text)

    def test_TC_G02_02_main_menu_state(self):
        """[ 주문 메뉴 ] + '선택: ' → MAIN_MENU."""
        state = self._feed_main_menu()
        self.assertIs(state, ScreenState.MAIN_MENU)

    def test_TC_G02_03_options_parsed(self):
        """주문 메뉴 옵션 5개가 정확히 파싱된다."""
        self._feed_main_menu()
        opts = self.sm.current_options
        self.assertEqual(len(opts), 5)
        self.assertEqual(opts[0], (1, '커피 주문'))
        self.assertEqual(opts[-1], (0, '처음 화면'))


class TestMultiOptionLine(unittest.TestCase):

    def test_TC_G02_04_inline_multi_option(self):
        """한 줄에 여러 옵션이 있어도 모두 파싱된다."""
        sm = GUIStateMachine()
        text = (
            f'{SEP}\n'
            '[ 관리자 메뉴 ]\n'
            '  1. 재고 보충     2. 상품 ON/OFF\n'
            '  3. 가격 변경     4. 현금 보유량 확인\n'
            '  5. 비밀번호 변경  6. 키오스크 종료\n'
            '  0. 관리자 메뉴 종료\n'
            '선택: '
        )
        sm.feed(text)
        nums = [n for n, _ in sm.current_options]
        self.assertIn(2, nums)
        self.assertIn(6, nums)
        self.assertIn(0, nums)
        self.assertEqual(len(nums), 7)


class TestSpecialPrompts(unittest.TestCase):

    def test_TC_G02_05_yn_confirm(self):
        """(y/n): 프롬프트 → YN_CONFIRM."""
        sm = GUIStateMachine()
        sm.feed('정말 비우시겠습니까? (y/n): ')
        self.assertIs(sm.current_state, ScreenState.YN_CONFIRM)

    def test_TC_G02_06_admin_auth(self):
        """'비밀번호:' 로 끝나면 → ADMIN_AUTH."""
        sm = GUIStateMachine()
        sm.feed(f'{SEP}\n관리자 비밀번호: ')
        self.assertIs(sm.current_state, ScreenState.ADMIN_AUTH)

    def test_TC_G02_07_numpad_replenish(self):
        """보충량 (0=뒤로) → NUMPAD."""
        sm = GUIStateMachine()
        sm.feed('보충량 (1~3000, 0=뒤로): ')
        self.assertIs(sm.current_state, ScreenState.NUMPAD)


class TestForceParse(unittest.TestCase):

    def test_TC_G02_08_idle_force_parse(self):
        """idle 화면은 프롬프트 없음 → force_parse() 로 IDLE 감지."""
        sm = GUIStateMachine()
        idle_text = (
            f'{SEP}\n'
            '   Micro-Factory Kiosk\n\n'
            '   화면을 터치하면 시작합니다.\n'
            f'{SEP}\n'
        )
        # feed 는 None 반환 (프롬프트 없음)
        result = sm.feed(idle_text)
        self.assertIsNone(result)
        # force_parse 로 강제 처리
        state = sm.force_parse()
        self.assertIs(state, ScreenState.IDLE)


class TestIngredientSelect(unittest.TestCase):

    def test_TC_G02_09_ing_select(self):
        """[ 원재료 목록 ] + '번호 선택 (0=뒤로): ' → ING_SELECT."""
        sm = GUIStateMachine()
        text = (
            f'{SEP}\n'
            '  [ 원재료 목록 ]\n'
            '  번호 ID     이름     현재 재고   최대\n'
            f'  {SEP}\n'
            '  1    bean  원두     2000g      5000g\n'
            '  2    milk  우유     5000ml    10000ml\n'
            '  번호 선택 (0=뒤로): '
        )
        state = sm.feed(text)
        self.assertIs(state, ScreenState.ING_SELECT)


if __name__ == '__main__':
    unittest.main(verbosity=2)
