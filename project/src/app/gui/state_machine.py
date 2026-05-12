"""
gui/state_machine.py — GUI-02

GUIStateMachine : CLI print() 출력을 누적·분석하여 현재 화면 상태와
                  선택 가능한 옵션 목록을 결정한다.
ScreenState     : 가능한 화면 상태 열거형
"""
import re
from enum import Enum, auto


class ScreenState(Enum):
    IDLE        = auto()   # 대기 화면
    MAIN_MENU   = auto()   # 주문 메뉴
    CUSTOMIZE   = auto()   # 옵션 선택 (상품 선택, 크기/온도/샷 등)
    CART        = auto()   # 장바구니
    PAYMENT     = auto()   # 결제 수단 선택
    CASH        = auto()   # 현금 투입
    CARD        = auto()   # 카드 결제
    ADMIN_AUTH  = auto()   # 관리자 비밀번호 입력
    ADMIN_MENU  = auto()   # 관리자 메뉴
    ING_SELECT  = auto()   # 원재료 목록 선택
    PROD_SELECT = auto()   # 상품 목록 선택
    YN_CONFIRM  = auto()   # y/n 확인
    NUMPAD      = auto()   # 숫자 입력 (수량/가격/보충량)
    RECEIPT     = auto()   # 영수증
    UNKNOWN     = auto()   # 미분류


class GUIStateMachine:
    """
    CLI stdout 텍스트를 받아 화면 상태를 추론한다.

    사용법:
        sm = GUIStateMachine()
        state = sm.feed(text)   # 프롬프트 감지 시 ScreenState 반환, 아니면 None
        state = sm.force_parse() # 타임아웃 등 외부 트리거로 강제 파싱 (idle 등)
        opts  = sm.current_options  # [(num, label), ...]
    """

    _PROMPTS = [
        '선택: ',
        '(y/n): ',
        '비밀번호: ',
        '뒤로): ',    # (0=뒤로): 과 ..., 0=뒤로): 모두 포함
        '(0=삭제): ',
        '아주세요...',
    ]
    _IDLE_MARKER = '화면을 터치하면 시작합니다.'
    _SEP         = '─' * 40

    # 숫자패드를 트리거하는 프롬프트 키워드
    _NUMPAD_KW = ('보충량', '새 수량', '새 가격', '수량 입력')

    # 옵션 그룹 헤더 집합 (커스텀 옵션 선택 화면)
    _OPT_GROUPS = {'크기', '온도', '샷', '당도', '크림', '맛', '성분', '수량(알)', '패키지'}

    # 헤더 → ScreenState 맵
    _HEADER_MAP = {
        '주문 메뉴':      ScreenState.MAIN_MENU,
        '커피 선택':      ScreenState.CUSTOMIZE,
        '구미 선택':      ScreenState.CUSTOMIZE,
        '장바구니':       ScreenState.CART,
        '수량 변경':      ScreenState.CART,
        '결제 수단 선택': ScreenState.PAYMENT,
        '현금 투입':      ScreenState.CASH,
        '관리자 메뉴':    ScreenState.ADMIN_MENU,
        '원재료 목록':    ScreenState.ING_SELECT,
        '상품 목록':      ScreenState.PROD_SELECT,
    }

    def __init__(self):
        self._buffer  = ''
        self._state   = ScreenState.UNKNOWN
        self._options: list[tuple[int, str]] = []

    # ── 공개 API ─────────────────────────────────────────────
    def feed(self, text: str) -> 'ScreenState | None':
        """
        텍스트를 버퍼에 추가한다.
        프롬프트가 감지되면 파싱 후 새 ScreenState 를 반환한다.
        프롬프트 없으면 None 을 반환한다.
        """
        self._buffer += text

        for p in self._PROMPTS:
            if self._buffer.endswith(p):
                self._parse()
                self._buffer = ''
                return self._state

        return None

    def force_parse(self) -> 'ScreenState':
        """
        버퍼를 즉시 파싱한다.
        idle 화면처럼 프롬프트 없이 입력을 기다리는 경우
        외부(타임아웃 등)에서 호출한다.
        """
        if self._buffer:
            self._parse()
            self._buffer = ''
        return self._state

    @property
    def current_state(self) -> ScreenState:
        return self._state

    @property
    def current_options(self) -> list:
        return list(self._options)

    # ── 내부 파싱 ────────────────────────────────────────────
    def _parse(self) -> None:
        text  = self._buffer
        lines = text.split('\n')

        # Idle 화면
        if self._IDLE_MARKER in text:
            self._state   = ScreenState.IDLE
            self._options = []
            return

        # 영수증
        if '영  수  증' in text:
            self._state   = ScreenState.RECEIPT
            self._options = []
            return

        # 헤더 [ ... ] 추출
        header = self._extract_header(lines)

        # 번호 옵션 파싱 (한 줄 다중 옵션 포함)
        self._options = self._extract_options(lines)

        # 마지막 줄로 프롬프트 종류 판별
        last = text.rstrip().split('\n')[-1] if text.strip() else ''

        if '(y/n)' in last:
            self._state = ScreenState.YN_CONFIRM
            return

        if '태그해 주세요' in last:
            self._state = ScreenState.CARD
            return

        if '비밀번호:' in last:
            self._state = ScreenState.ADMIN_AUTH
            return

        if '(0=삭제)' in last:
            self._state = ScreenState.NUMPAD
            return

        if '뒤로)' in last and any(k in last for k in self._NUMPAD_KW):
            self._state = ScreenState.NUMPAD
            return

        # 헤더 기반 상태 결정
        if header in self._OPT_GROUPS:
            self._state = ScreenState.CUSTOMIZE
        elif header in self._HEADER_MAP:
            self._state = self._HEADER_MAP[header]
        else:
            self._state = ScreenState.UNKNOWN

    @staticmethod
    def _extract_header(lines: list[str]) -> 'str | None':
        for line in lines:
            m = re.search(r'\[ (.+?) \]', line)
            if m:
                return m.group(1).strip()
        return None

    @staticmethod
    def _extract_options(lines: list[str]) -> list[tuple[int, str]]:
        """한 줄 내 다중 옵션을 포함하여 (번호, 라벨) 리스트를 반환한다."""
        opts: list[tuple[int, str]] = []
        seen: set[int] = set()
        for line in lines:
            for m in re.finditer(r'(\d+)\.\s+(.+?)(?=\s{2,}\d+\.|\s*$)', line):
                n   = int(m.group(1))
                lbl = m.group(2).strip()
                if lbl and n not in seen:
                    opts.append((n, lbl))
                    seen.add(n)
        return opts
