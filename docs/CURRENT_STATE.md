# CURRENT_STATE.md

> Last Update: 2026-05-26
> Phase: **완료** — EDK 전체 구현 + 테스트 + 패키징 완료

---

## 프로젝트 개요

**EDK (Erica Drug King)** — 증상 기반 OTC 의약품 키오스크

- 언어/런타임: Python 3.10+
- GUI 프레임워크: PyQt6 (스크린 기반 탐색)
- TTS: edge-tts + pygame
- 빌드: setuptools (pyproject.toml)

> ⚠️ **주의**: 이 프로젝트는 Coffee/Gummy 도메인과 **무관**합니다.
> `백업(__STEP12__)` 디렉터리에 구버전 코드가 보존되어 있으나 현재 활성 코드베이스는 `project/src`의 EDK 구현입니다.

---

## 브랜치 상태

| 브랜치 | 역할 | 상태 |
|--------|------|------|
| `main` | 프로덕션 | 안정 버전 |
| `develop` | 통합 | 모든 기능 병합 완료 |
| `feature/*` | 작업 브랜치 | 전부 develop에 병합됨 |

### 병합 완료 PR 이력

| PR | 브랜치 | 내용 | 병합일 |
|----|--------|------|--------|
| #11 | feature/gui-edk-01-06 → develop | GUI 전체 구현 (KioskWindow + 11개 스크린) | 2026-05-26 |
| #13 | feature/edk-tests → develop | 테스트 전면 재작성 (EDK 도메인) | 2026-05-26 |
| #14 | feature/packaging → develop | pyproject.toml + README.md | 2026-05-26 |

---

## 구현 완료 항목

### 모델 (`project/src/model/`)

| 파일 | 클래스 | 설명 |
|------|--------|------|
| medicine.py | `Medicine` | id, name, price, available, symptoms 목록 |
| symptom.py | `Symptom`, `SymptomGroup` | 증상 + 응급 증상 그룹 |
| cart.py | `Cart` | 장바구니 (add/remove/clear/update) |
| order_item.py | `OrderItem` | 품목 (medicine, {}, qty) |
| cash_payment.py | `CashPayment` | 현금 결제 + 잔돈 계산 |

### 컨트롤러 (`project/src/controller/`)

| 파일 | 클래스 | 메서드 |
|------|--------|--------|
| drug_controller.py | `DrugController` | `get_all_medicines`, `get_medicines_by_symptom`, `get_symptoms`, `get_symptom_groups`, `get_medicine_by_id` |

### GUI (`project/src/view/gui/`)

| 파일 | 클래스 | 설명 |
|------|--------|------|
| kiosk_window.py | `KioskWindow(controller, cart, change_reserve)` | 메인 윈도우, 스크린 전환 관리 |
| screens/idle_screen.py | `IdleScreen` | 대기 화면 |
| screens/symptom_select_screen.py | `SymptomSelectScreen` | 증상 선택 그리드 |
| screens/medicine_list_screen.py | `MedicineListScreen` | 의약품 목록 (증상 필터) |
| screens/medicine_detail_screen.py | `MedicineDetailScreen` | 의약품 상세 + 장바구니 추가 |
| screens/emergency_screen.py | `EmergencyScreen` | 응급 증상 안내 |
| screens/cart_screen.py | `CartScreen` | 장바구니 확인 |
| screens/payment_method_screen.py | `PaymentMethodScreen` | 결제 수단 선택 |
| screens/cash_payment_screen.py | `CashPaymentScreen` | 현금 투입 처리 |
| screens/receipt_screen.py | `ReceiptScreen` | 영수증 |
| screens/admin_auth_screen.py | `AdminAuthScreen` | 관리자 PIN 인증 |
| screens/admin_menu_screen.py | `AdminMenuScreen` | 관리자 메뉴 |

### CLI (`project/src/view/cli/`)

| 파일 | 클래스 | 설명 |
|------|--------|------|
| cli_view.py | `CLIView` | 관리자 전용 터미널 뷰 |

### 서비스 (`project/src/service/`)

| 파일 | 클래스 | 설명 |
|------|--------|------|
| voice_service.py | `VoiceService` | edge-tts + pygame TTS |

### 데이터 (`project/src/data/`)

- `medicines.json` — 의약품 데이터
- `symptoms.json` — 증상 데이터
- `admin_config.json` — 관리자 비밀번호

### 패키징 (`project/`)

| 파일 | 설명 |
|------|------|
| pyproject.toml | setuptools 빌드, pytest 설정, 의존성 정의 |
| README.md | 설치/실행/테스트/구조 문서 |
| build_mac.sh | macOS 빌드 스크립트 |
| build_windows.ps1 | Windows 빌드 스크립트 |

---

## 테스트 현황 (`project/tests/`)

| 파일 | 대상 | 비고 |
|------|------|------|
| conftest.py | 픽스처 | DrugController, Medicine, Symptom, Cart, mock_window |
| test_cart.py | Cart + OrderItem | Medicine 기반, 재고 확인 없음 |
| test_medicine.py | Medicine | 속성, available 플래그 |
| test_drug_controller.py | DrugController | 5개 메서드 |
| test_data_manager.py | DataManager | JSON I/O |
| test_payment.py | CashPayment | 투입/완료/잔돈 계산 |
| test_stats.py | Stats | 통계 |
| test_exceptions.py | 예외 클래스 | |
| test_edk_integration.py | 통합 | 장바구니+증상+결제 플로우 |
| test_gui_app.py | KioskWindow | 생성, 화면 전환, 장바구니 초기화 |
| test_gui_screens.py | 11개 스크린 전체 | pytest-qt 필요 |
| test_admin_cash.py | CLIView 관리자 메뉴 | builtins.input mock |

### 실행 명령

```bash
cd project
pytest          # 전체
pytest -v       # 상세 출력
```

> pytest 설정은 `pyproject.toml`의 `[tool.pytest.ini_options]`에 정의됨.
> `testpaths = ["tests"]`, `pythonpath = ["src"]`

---

## KioskWindow 핵심 설계 사항

- 생성자 서명: `KioskWindow(controller, cart, change_reserve)`
- `cart`와 `change_reserve`는 **window 필드** (controller 필드 아님)
- `window._active_payment`: CashPayment 인스턴스 저장 위치
- `window._current_symptom_name`: 증상 목록 → 상세 → 뒤로 가기 시 사용
- `__init__`에서 `go_to_idle()` 호출 → 장바구니 초기화됨

---

## 남은 작업

현재 알려진 미완료 항목 없음.

다음 AI 세션 시작 전 확인 권장 사항:
- `develop` → `main` 최종 병합 여부
- 실제 하드웨어(키오스크) 연동 테스트 여부

---

## Source of Truth Documents

- [requirements.md](requirements.md) ✅
- [scope.md](scope.md) ✅
- [terminology.md](terminology.md) ✅
- [system_flow.md](system_flow.md) ✅
- [architecture.md](architecture.md) ✅ *(일부 구버전 내용 포함 가능 — 코드 우선)*
- [test_strategy.md](test_strategy.md) ✅
- [gui_architecture.md](gui_architecture.md) ✅
