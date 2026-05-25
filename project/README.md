# EDK — Erica Drug King

증상 기반 OTC(일반의약품) 키오스크 시스템입니다.  
사용자가 증상을 선택하면 적합한 의약품을 추천하고, 현금 결제까지 처리합니다.

---

## 목차

1. [사전 요구사항](#사전-요구사항)
2. [설치](#설치)
3. [실행](#실행)
4. [테스트](#테스트)
5. [빌드](#빌드)
6. [디렉터리 구조](#디렉터리-구조)
7. [화면 흐름](#화면-흐름)
8. [관리자 메뉴](#관리자-메뉴)

---

## 사전 요구사항

| 항목 | 버전 |
|------|------|
| Python | 3.10 이상 |
| pip | 최신 권장 |
| 오디오 드라이버 | TTS 사용 시 필요 |

---

## 설치

```bash
# 1. 저장소 클론
git clone https://github.com/yj2trigger/pmg-ic-pbl.git
cd pmg-ic-pbl/project

# 2. 가상환경 생성 및 활성화
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. 의존성 설치 (런타임)
pip install .

# 4. 개발용 의존성 추가 설치 (테스트 포함)
pip install .[dev]
```

---

## 실행

### GUI 모드 (키오스크)

```bash
cd project
python -m src.main
```

### CLI 모드 (관리자 도구)

```bash
cd project
python -m src.main --cli
```

---

## 테스트

```bash
cd project
pytest
```

상세 출력:

```bash
pytest -v
```

특정 파일만 실행:

```bash
pytest tests/test_cart.py -v
```

> **참고**: GUI 테스트(`test_gui_*.py`)는 `pytest-qt`가 필요합니다.  
> TTS / pygame 관련 모듈은 테스트 시 자동으로 mock 처리됩니다.

---

## 빌드

```bash
cd project
pip install build
python -m build
```

`dist/` 디렉터리에 `.whl` 및 `.tar.gz` 파일이 생성됩니다.

---

## 디렉터리 구조

```
project/
├── src/
│   ├── main.py                  # 진입점
│   ├── controller/
│   │   └── drug_controller.py   # 비즈니스 로직
│   ├── model/
│   │   ├── medicine.py
│   │   ├── symptom.py
│   │   ├── cart.py
│   │   ├── order_item.py
│   │   └── cash_payment.py
│   ├── view/
│   │   ├── gui/
│   │   │   ├── kiosk_window.py  # 메인 윈도우
│   │   │   └── screens/         # 각 화면 위젯
│   │   └── cli/
│   │       └── cli_view.py      # CLI 관리자 뷰
│   ├── data/
│   │   ├── medicines.json
│   │   ├── symptoms.json
│   │   └── admin_config.json
│   └── service/
│       └── voice_service.py     # edge-tts + pygame TTS
├── tests/
│   ├── conftest.py
│   ├── test_cart.py
│   ├── test_gui_app.py
│   ├── test_gui_screens.py
│   ├── test_admin_cash.py
│   └── test_edk_integration.py
└── pyproject.toml
```

---

## 화면 흐름

```
[대기 화면]
    │
    ▼
[증상 선택 화면] ──────────────────────┐
    │                                  │
    ▼                                  │
[의약품 목록 화면]   [응급 증상 화면]  │
    │                    ▲             │
    ▼                    │             │
[의약품 상세 화면] ──────┘             │
    │                                  │
    ▼                                  │
[장바구니 화면] ◄──────────────────────┘
    │
    ▼
[결제 수단 선택]
    │
    ▼
[현금 결제 화면]
    │
    ▼
[영수증 화면]
    │
    ▼
[대기 화면]
```

관리자 접근:

```
[대기 화면] → 관리자 버튼 → [관리자 인증] → [관리자 메뉴]
```

---

## 관리자 메뉴

### GUI 관리자 메뉴

| 기능 | 설명 |
|------|------|
| 의약품 ON/OFF | 판매 중지 / 재개 |
| 가격 변경 | 선택 의약품 판매가 변경 |
| 현금 보유량 | 권종별 잔액 확인 및 조정 |
| 비밀번호 변경 | 관리자 PIN 변경 |

### CLI 관리자 메뉴

CLI 모드(`--cli`)로 실행하면 터미널에서 관리자 기능을 직접 사용할 수 있습니다.

```
관리자 메뉴
1. 의약품 목록 보기
2. 의약품 ON/OFF 전환
3. 가격 변경
4. 현금 보유량 확인
5. 현금 보유량 변경
6. 비밀번호 변경
0. 종료
```

> 기본 관리자 비밀번호는 `data/admin_config.json`에서 설정합니다.
