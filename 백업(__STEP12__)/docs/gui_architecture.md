# GUI 확장 아키텍처 (Architecture)

> 작성일: 2026-05-12
> 상태: GUI 개발 진행 중

---

## 1. 화면 분할 구조

```
┌────────────────────────────────────────────────────────┐
│                    메인 윈도우 (tkinter)                 │
│                                                        │
│  ┌──────────────────┐  ┌───────────────────────────┐  │
│  │   GUI 영역 (1/3) │  │  CLI 로그 영역 (2/3)       │  │
│  │                  │  │                           │  │
│  │  터치 버튼        │  │  기존 print() 출력이       │  │
│  │  메뉴 카드        │  │  실시간으로 표시됨         │  │
│  │  입력 패드        │  │  (Read-only ScrolledText) │  │
│  │                  │  │                           │  │
│  └──────────────────┘  └───────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 2. 모듈 구조

```
project/src/app/
├── (기존 — 수정 없음)
│   ├── exceptions.py
│   ├── ingredient.py
│   ├── product.py
│   ├── cart.py
│   ├── payment.py
│   ├── stats.py
│   ├── data_manager.py
│   ├── kiosk_controller.py
│   ├── cli_view.py
│   └── main.py
│
└── (신규 — GUI 레이어)
    ├── gui/
    │   ├── __init__.py
    │   ├── app.py           # GUIApp: 최상위 윈도우 & 레이아웃
    │   ├── log_panel.py     # LogPanel: stdout 리다이렉터 + ScrolledText
    │   ├── control_panel.py # ControlPanel: 버튼/카드 패널 컨테이너
    │   ├── state_machine.py # GUIStateMachine: CLI 출력 파싱 → 화면 전환
    │   └── widgets/
    │       ├── numpad.py    # 터치 숫자패드
    │       ├── menu_card.py # 메뉴 카드 버튼
    │       └── yn_dialog.py # Y/N 확인 다이얼로그
    └── gui_main.py          # GUI 진입점 (main.py 대체)
```

---

## 3. 핵심 설계 원칙

### 3-1. Humble Object Pattern
- **Model** (비즈니스 로직): `KioskController` — 기존 그대로
- **View** (GUI): `GUIApp` — Controller를 호출만 함
- **Presenter** (상태 머신): `GUIStateMachine` — CLI 출력을 파싱해 GUI 상태 결정

### 3-2. Stdout 리다이렉션
```python
# 기존 print() → LogPanel의 ScrolledText로 출력
sys.stdout = StdoutRedirector(log_panel_widget)
```
- CLI 코드(`cli_view.py`, `kiosk_controller.py`)의 `print()` 는 **수정하지 않음**
- `StdoutRedirector`가 `write()`를 오버라이드하여 TextWidget에 삽입

### 3-3. 상태 머신
```
CLI 출력 → StdoutRedirector.write() → GUIStateMachine.feed(text)
                                              ↓
                                    현재 화면 상태 결정
                                              ↓
                                    ControlPanel.render(state)
```

---

## 4. 의존성 방향

```
gui_main.py
    ↓
GUIApp (app.py)
    ├── LogPanel (log_panel.py)          ← stdout 리다이렉터
    ├── ControlPanel (control_panel.py)  ← 버튼 렌더
    └── GUIStateMachine (state_machine.py)
            ↓
        KioskController (기존)
```

---

## 5. GUI Unit 구현 계획

| Unit | 파일 | 책임 | 상태 |
|------|------|------|------|
| GUI-01 | log_panel.py | 레이아웃 뼈대 + stdout 리다이렉터 | ⬜ 대기 |
| GUI-02 | state_machine.py | CLI 출력 파싱 → 상태 전환 | ⬜ 대기 |
| GUI-03 | widgets/numpad.py | 터치 숫자패드 | ⬜ 대기 |
| GUI-04 | widgets/menu_card.py | 메뉴 카드 버튼 | ⬜ 대기 |
| GUI-05 | control_panel.py | 상태별 버튼 렌더링 | ⬜ 대기 |
| GUI-06 | app.py | 통합 및 최종 연결 | ⬜ 대기 |
| GUI-07 | gui_main.py | 진입점 | ⬜ 대기 |
