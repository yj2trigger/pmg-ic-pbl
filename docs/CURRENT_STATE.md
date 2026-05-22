# CURRENT_STATE.md

> Last Update: 2026-05-23
> Phase: 도메인 전환 — EDK(Erica Drug King) 리팩터링 시작

---

## ⚠️ 프로젝트 방향 전환 공지

**기존**: Micro-Factory Kiosk (커피/영양구미 판매)
**변경**: EDK — 증상 선택 기반 일반의약품 정보 제공 키오스크

기존 PyQt6 GUI 아키텍처(QStackedWidget, screens/, voice_service 등)는 **그대로 재활용**하고,
도메인(상품 → 의약품, 결제 → 제거, 옵션 → 증상)만 교체한다.

---

## Current Active Unit

**EDK-01**: `product.py` → `medicine.py` 리팩터링
- `Coffee`, `Gummy` → `Medicine` 클래스로 교체
- `product_type` → `symptom_category` 개념으로 전환

---

## ✅ 재활용 가능한 완료 유닛 (수정 불필요)

| Unit | 파일 | 비고 |
|------|------|------|
| UNIT-01 | exceptions.py | 그대로 재활용 |
| UNIT-02 | ingredient.py | 의약품 재고 수량으로 재활용 |
| UNIT-09 | data_manager.py | 의약품 JSON 데이터 관리로 재활용 |
| GUI-APP | gui/app.py | 그대로 재활용 |
| GUI-WIN | gui/main_window.py | 네비게이션 API 수정 필요 |
| GUI-VOICE | gui/voice_service.py | 그대로 재활용 |
| GUI-S09 | gui/screens/admin_auth.py | 그대로 재활용 |

---

## 🔄 EDK 전환 작업 목록

### Core 레이어 전환

| 작업 | 대상 파일 | 내용 | 상태 |
|------|----------|------|------|
| EDK-01 | product.py → medicine.py | Coffee/Gummy → Medicine 클래스 | 🔵 시작 |
| EDK-02 | cart.py | 결제 로직 제거, 관심 의약품 선택 목록으로 단순화 | ⬜ 대기 |
| EDK-03 | payment.py | 제거 (정보 제공 서비스 — 결제 불필요) | ⬜ 대기 |
| EDK-04 | kiosk_controller.py → drug_controller.py | 증상→의약품 매핑 로직으로 전환 | ⬜ 대기 |
| EDK-05 | data_manager.py | medicines.json / symptoms.json 데이터 구조 적용 | ⬜ 대기 |
| EDK-06 | main.py | 의약품 데이터 초기화 로직으로 교체 | ⬜ 대기 |
| EDK-07 | cli_view.py | 증상 선택 → 의약품 정보 탐색 흐름으로 교체 | ⬜ 대기 |

### GUI 레이어 전환

| 작업 | 기존 파일 | 신규 파일 | 내용 | 상태 |
|------|----------|----------|------|------|
| GUI-EDK-01 | main_window.py | main_window.py | 네비게이션 API를 EDK 화면 흐름으로 교체 | ⬜ 대기 |
| GUI-EDK-02 | main_menu.py | symptom_select.py | 증상 카테고리 선택 화면 | ⬜ 대기 |
| GUI-EDK-03 | product_list.py | medicine_list.py | 의약품 목록 화면 | ⬜ 대기 |
| GUI-EDK-04 | customize.py | medicine_detail.py | 의약품 상세 정보 화면 | ⬜ 대기 |
| GUI-EDK-05 | receipt.py | caution.py | 복용 주의사항 안내 화면 | ⬜ 대기 |
| GUI-EDK-06 | (없음) | emergency.py | 응급 상황 안내 화면 (신규) | ⬜ 대기 |
| GUI-EDK-07 | admin_menu.py | admin_menu.py | 의약품 정보/재고 관리로 수정 | ⬜ 대기 |
| GUI-EDK-08 | cart.py | (제거) | 결제 흐름 제거 | ⬜ 대기 |
| GUI-EDK-09 | payment_method.py | (제거) | 결제 흐름 제거 | ⬜ 대기 |
| GUI-EDK-10 | cash_payment.py | (제거) | 결제 흐름 제거 | ⬜ 대기 |

---

## 목표 GUI 구조 (EDK 전환 후)

```
src/app/
├── main.py
├── drug_controller.py       # KioskController → DrugController
├── cli_view.py              # 증상 탐색 CLI 뷰
├── medicine.py              # Medicine 클래스 (Product 교체)
├── ingredient.py            # 재고 수량 (재활용)
├── data_manager.py          # medicines.json / symptoms.json
├── exceptions.py            # 재활용
└── gui/
    ├── app.py               # 재활용
    ├── main_window.py       # 네비게이션 API 교체
    ├── voice_service.py     # 재활용
    └── screens/
        ├── idle.py              # 재활용
        ├── symptom_select.py    # 신규 (main_menu 교체)
        ├── medicine_list.py     # 신규 (product_list 교체)
        ├── medicine_detail.py   # 신규 (customize 교체)
        ├── caution.py           # 신규 (receipt 교체)
        ├── emergency.py         # 신규 추가
        ├── admin_auth.py        # 재활용
        └── admin_menu.py        # 수정
```

---

## 데이터 파일 구성 (EDK)

| 파일 | 내용 |
|------|------|
| `medicines.json` | 의약품 목록 (이름, 효능, 복용법, 주의사항, 재고, 증상 카테고리) |
| `symptoms.json` | 증상 카테고리 정의 및 의약품 매핑 |
| `admin_config.json` | 관리자 비밀번호 (재활용) |

---

## Blocked Units

없음

---

## Current Risks

- 기존 테스트(test_*.py)가 구 도메인(커피/구미) 기반으로 작성되어 있어 전환 시 테스트 재작성 필요
- payment.py 관련 테스트 전체 폐기 예정

---

## 실행 방법

```bash
# CLI 모드 (project/ 디렉토리 안에서)
python -m app.main

# GUI 모드
python -m app.main --gui
```

---

## Source of Truth Documents

- requirements.md ✅ 업데이트 완료
- scope.md ✅ 업데이트 완료
- terminology.md 🔄 업데이트 필요
- system_flow.md 🔄 업데이트 필요
- architecture.md 🔄 업데이트 필요
- test_strategy.md 🔄 업데이트 필요
