# CURRENT_STATE.md

> Last Update: 2026-05-23
> Phase: GUI 구현 완료 — 패키징 / 마무리 단계

---

## Current Active Unit

GUI 전체 구현 완료. 다음 단계: 패키징 설정(pyproject.toml + README.md) 및 discount.py 후순위 구현

---

## Completed Units

### Core 레이어

| Unit | 파일 | 테스트 | 완료일 |
|------|------|--------|--------|
| UNIT-01 | exceptions.py | 16/16 PASS | 2026-05-11 |
| UNIT-02 | ingredient.py | 12/12 PASS | 2026-05-12 |
| UNIT-03 | product.py | 5/5 PASS | 2026-05-12 |
| UNIT-04+05 | cart.py (recipe 통합) | 35/35 PASS | 2026-05-12 |
| UNIT-06 | payment.py | 35/35 PASS | 2026-05-12 |
| UNIT-08 | stats.py | 12/12 PASS | 2026-05-12 |
| UNIT-09 | data_manager.py | 8/8 PASS | 2026-05-12 |
| UNIT-10 | kiosk_controller.py | 15/15 PASS | 2026-05-12 |
| UNIT-11 | cli_view.py | 수동 테스트 (IO 기반) | 2026-05-12 |
| UNIT-12 | main.py | 임포트 검증 완료 | 2026-05-12 |
| 시나리오 | test_scenarios.py | 29/29 PASS | 2026-05-12 |

### GUI 레이어 (PyQt6 기반 — 실제 구현 완료)

| Unit | 파일 | 설명 | 상태 |
|------|------|------|------|
| GUI-APP | gui/app.py | QApplication 진입점, run_gui() | ✅ 완료 |
| GUI-WIN | gui/main_window.py | KioskWindow (QStackedWidget), 전체 화면 네비게이션 API, 글로벌 스타일시트 | ✅ 완료 |
| GUI-VOICE | gui/voice_service.py | VoiceService — TTS 음성 안내 | ✅ 완료 |
| GUI-S01 | gui/screens/idle.py | 대기 화면 | ✅ 완료 |
| GUI-S02 | gui/screens/main_menu.py | 메인 메뉴 (커피 / 영양구미 선택) | ✅ 완료 |
| GUI-S03 | gui/screens/product_list.py | 상품 목록 화면 | ✅ 완료 |
| GUI-S04 | gui/screens/customize.py | 옵션 커스터마이징 화면 | ✅ 완료 |
| GUI-S05 | gui/screens/cart.py | 장바구니 화면 | ✅ 완료 |
| GUI-S06 | gui/screens/payment_method.py | 결제 수단 선택 화면 | ✅ 완료 |
| GUI-S07 | gui/screens/cash_payment.py | 현금 결제 화면 | ✅ 완료 |
| GUI-S08 | gui/screens/receipt.py | 영수증 화면 | ✅ 완료 |
| GUI-S09 | gui/screens/admin_auth.py | 관리자 인증 화면 | ✅ 완료 |
| GUI-S10 | gui/screens/admin_menu.py | 관리자 메뉴 (재고/가격/현금/비밀번호 관리) | ✅ 완료 |

---

## 실제 GUI 구조 (코드 기준)

```
src/app/
├── main.py                  # 진입점 (--gui 플래그 or frozen → GUI, 기본 → CLI)
├── kiosk_controller.py      # 비즈니스 로직 컨트롤러
├── cli_view.py              # CLI 뷰
├── cart.py / payment.py / product.py / ingredient.py
├── stats.py / data_manager.py / exceptions.py
└── gui/
    ├── app.py               # run_gui() — QApplication 래퍼
    ├── main_window.py       # KioskWindow — QStackedWidget + 네비게이션 API
    ├── voice_service.py     # VoiceService — TTS 음성 안내
    ├── screens/
    │   ├── idle.py          # 대기 화면
    │   ├── main_menu.py     # 메인 메뉴
    │   ├── product_list.py  # 상품 목록
    │   ├── customize.py     # 옵션 커스터마이징
    │   ├── cart.py          # 장바구니
    │   ├── payment_method.py # 결제 수단 선택
    │   ├── cash_payment.py  # 현금 결제
    │   ├── receipt.py       # 영수증
    │   ├── admin_auth.py    # 관리자 인증
    │   └── admin_menu.py    # 관리자 메뉴
    └── widgets/             # (현재 비어있음 — 향후 공용 위젯 추가 예정)
```

---

## 주요 변경사항 (계획 대비 실제)

| 항목 | 계획 (구 docs) | 실제 구현 |
|------|---------------|----------|
| GUI 프레임워크 | 미정 (log_panel 등 계획) | **PyQt6 QStackedWidget** |
| 화면 구조 | log_panel, state_machine 등 | **screens/ 10개 화면으로 분리** |
| 음성 안내 | 계획 없음 | **VoiceService (TTS) 추가** |
| 진입점 | gui_main.py 예정 | **main.py --gui 플래그로 통합** |
| 관리자 기능 | 별도 계획 없음 | **admin_auth + admin_menu 구현** |

---

## Blocked Units

없음

---

## Current Risks

없음

---

## Pending

| 항목 | 파일 | 우선순위 |
|------|------|----------|
| 패키징 설정 | pyproject.toml + README.md | 🔼 높음 |
| 할인 정책 | discount.py | 🔽 낮음 (시간 여유 시 구현) |
| 공용 위젯 | gui/widgets/ | 🔽 낮음 (필요 시 추가) |

---

## Last Verified Tests

- tests/test_exceptions.py — 16/16 PASS
- tests/test_ingredient.py — 12/12 PASS
- 실행 명령 (cmd): `set PYTHONPATH=src && python -m unittest discover -s tests`
- 실행 명령 (PowerShell): `$env:PYTHONPATH="src"; python -m unittest discover -s tests`
- (`project/` 디렉토리 안에서 실행)
- GUI 실행: `python -m app.main --gui` (project/ 디렉토리 안에서)

---

## Source of Truth Documents

- requirements.md ✅
- scope.md ✅
- terminology.md ✅
- system_flow.md ✅
- architecture.md ✅ (gui_architecture.md 별도 존재)
- test_strategy.md ✅
