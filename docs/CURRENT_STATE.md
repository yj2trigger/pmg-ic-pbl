# CURRENT_STATE.md

> Last Update: 2026-05-12
> Phase: STEP 10 — GUI 확장 시작 / GUI-01 대기

---

## Current Active Unit

GUI-01: 레이아웃 뼈대 + StdoutRedirector (승인 대기)

---

## Completed Units

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

---

## Blocked Units

없음

---

## Current Risks

없음

---

## Last Verified Tests

- tests/test_exceptions.py — 16/16 PASS
- tests/test_ingredient.py — 12/12 PASS
- 실행 명령 (cmd): `set PYTHONPATH=src && python -m unittest discover -s tests`
- 실행 명령 (PowerShell): `$env:PYTHONPATH="src"; python -m unittest discover -s tests`
- (`project/` 디렉토리 안에서 실행)

---

## Implementation Order

| 순서 | Unit | 파일 | 상태 |
|------|------|------|------|
| 01 | 예외 클래스 | exceptions.py | ✅ 완료 |
| 02 | 원재료 | ingredient.py | ✅ 완료 |
| 03 | 상품/옵션 | product.py | ✅ 완료 |
| 04+05 | 장바구니 + 재고확인 | cart.py (recipe 통합) | ✅ 완료 |
| 06 | 결제/잔돈 | payment.py | ✅ 완료 |
| 07 | 할인 정책 | discount.py | ⏭ 후순위 (시간 남으면 구현) |
| 08 | 통계 | stats.py | ✅ 완료 |
| 09 | JSON I/O | data_manager.py | ✅ 완료 |
| 10 | 컨트롤러 | kiosk_controller.py | ✅ 완료 |
| 11 | CLI 뷰 | cli_view.py | ✅ 완료 |
| 12 | 진입점 | main.py | ✅ 완료 |
| 13 | 패키징 설정 | pyproject.toml + README.md | ⬜ 대기 |

---

## Next Recommended Unit

GUI-01: log_panel.py (레이아웃 뼈대 + StdoutRedirector)

---

## GUI Implementation Order

| 순서 | Unit | 파일 | 상태 |
|------|------|------|------|
| GUI-01 | 레이아웃 + stdout 리다이렉터 | gui/log_panel.py | 🔵 대기 |
| GUI-02 | CLI 출력 파싱 상태 머신 | gui/state_machine.py | ⬜ 대기 |
| GUI-03 | 숫자패드 위젯 | gui/widgets/numpad.py | ⬜ 대기 |
| GUI-04 | 메뉴 카드 위젯 | gui/widgets/menu_card.py | ⬜ 대기 |
| GUI-05 | 컨트롤 패널 (상태별 렌더) | gui/control_panel.py | ⬜ 대기 |
| GUI-06 | 메인 앱 통합 | gui/app.py | ⬜ 대기 |
| GUI-07 | GUI 진입점 | gui/gui_main.py | ⬜ 대기 |

---

## Source of Truth Documents

- requirements.md ✅
- scope.md ✅
- terminology.md ✅
- system_flow.md ✅
- architecture.md ✅
- test_strategy.md ✅