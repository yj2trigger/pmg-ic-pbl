# EDK — Erica Drug King

증상을 입력하면 적합한 OTC 의약품을 추천하는 키오스크 애플리케이션입니다.  
PyQt6 GUI 또는 CLI 모드로 실행할 수 있으며, PyInstaller로 단독 실행 파일로 빌드할 수 있습니다.

---

## 요구사항

| 항목 | 버전 |
|------|------|
| Python | 3.10 이상 |
| OS | Windows 10/11, macOS 12이상 |

---

## 설치

```bash
# project/ 디렉토리에서 실행
cd project

# 의존성 설치 (실행 환경)
pip install -r requirements.txt

# 또는 pyproject.toml 사용 (dev 포함)
pip install -e \".[dev]\"
```

---

## 실행

### CLI 모드

```bash
cd project
python src/app/main.py
```

### GUI 모드

```bash
cd project
python src/app/main.py --gui
```

> **카리우스 한국어 TTS** `edge-tts`를 사용합니다. 인터넷 연결이 없으면 음성 기능이 작동하지 않습니다 (나머지 기능은 정상 작동).

---

## 테스트

```bash
cd project
pytest
```

`pyproject.toml`의 `[tool.pytest.ini_options]`에서 `testpaths`과 `pythonpath`을 자동으로 해서합니다.  
GUI 테스트는 `QT_QPA_PLATFORM=offscreen`으로 디스플레\ 없이 실행됩니다.

---

## 빌드 (단독 실행 파일)

### Windows

```powershell
cd project
.\\build_windows.ps1
# 출력: dist\\kiosk.exe
```

### macOS

```bash
cd project
bash build_mac.sh
# 출력: dist/kiosk
```

---

## 디렉토리 구조

```
project/
├── src/
│   └── app/
│       ├── main.py              # 진입점 (CLI / GUI 선택)
│       ├── drug_controller.py   # 증상→의약품 조회
│       ├── medicine.py          # Medicine 도메인
│       ├── symptom.py           # Symptom / SymptomGroup
│       ├── cart.py              # OrderItem, Cart
│       ├── payment.py           # CashPayment, CardPayment, ChangeReserve
│       ├── data_manager.py      # JSON 읽기/쓰기
│       ├── cli_view.py          # CLI 인터페이스
│       ├── stats.py             # 판매 통계
│       ├── exceptions.py        # 커스텀 예외
│       ├── data/                # JSON 데이터 (medicines.json 등)
│       └── gui/
│           ├── app.py             # QApplication 진입점
│           ├── main_window.py     # KioskWindow + 네비게이션 API
│           ├── voice_service.py   # edge-tts TTS
│           └── screens/           # 화면별 QWidget
├── tests/
├── pyproject.toml
├── requirements.txt
├── build_windows.ps1
└── build_mac.sh
```

---

## 주요 화면 흐름

```
[대기 화면]
    ↓ 터치
[증상 선택]  →  응급 증상이면 [응급 경고 (119)]
    ↓
[의약품 목록]  →  [의약품 상세] → [장바구니]
    ↓
[결제 수단 선택]  →  현금 / 카드
    ↓
[영수증]  →  [대기 화면]
```

---

## 관리자 메뉴

증상 선택 화면 하단의 **관리자** 버튼 또는 CLI에서 메뉴 4번으로 접근합니다.

| 기능 | 설명 |
|------|------|
| 의약품 ON/OFF | 판매 중지 / 재개 |
| 가격 변경 | 선택 의약품 판매가 변경 |
| 현금 보유량 | 권종별 \uc7