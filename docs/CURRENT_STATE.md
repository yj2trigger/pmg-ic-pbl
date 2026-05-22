# CURRENT_STATE.md

> Last Update: 2026-05-23
> Phase: 도메인 전환 — EDK(Erica Drug King) 리팩터링 시작

---

## ⚠️ 프로젝트 방향 전환 공지

**기존**: Micro-Factory Kiosk (커피/영양구미 판매)
**변경**: EDK — 증상 선택 기반 일반의약품/영양제 **실제 판매** 키오스크

### 핵심 전환 원칙
- 기존 PyQt6 GUI 아키텍처(QStackedWidget, screens/, voice_service)는 **그대로 재활용**
- **결제 시스템(payment.py, cart.py, ChangeReserve)은 유지** — 실제 판매이므로 필수
- 도메인 교체: 상품(커피/구미) → 의약품/영양제, 옵션 → 증상 카테고리
- 취급 품목: 영양제 + 일반의약품만 (전문의약품 제외)

---

## Current Active Unit

**EDK-01**: `product.py` → `medicine.py` 리팩터링
- `Coffee`, `Gummy` → `Medicine` 클래스로 교체
- `product_type` → `symptom_category` 개념으로 전환

---

## ✅ 재활용 확정 유닛 (수정 불필요)

| 파일 | 재활용 방식 |
|------|-----------|
| exceptions.py | 그대로 재활용 |
| ingredient.py | 의약품/영양제 재고로 재활용 |
| cart.py | **그대로 재활용** (실제 판매, 장바구니 필요) |
| payment.py | **그대로 재활용** (현금/카드 결제 필요) |
| data_manager.py | 의약품 JSON 데이터 관리로 재활용 |
| gui/app.py | 그대로 재활용 |
| gui/voice_service.py | 그대로 재활용 |
| gui/screens/admin_auth.py | 그대로 재활용 |
| gui/screens/cart.py | **그대로 재활용** |
| gui/screens/payment_method.py | **그대로 재활용** |
| gui/screens/cash_payment.py | **그대로 재활용** |
| gui/screens/receipt.py | **그대로 재활용** |

---

## 🔄 EDK 전환 작업 목록

### Core 레이어 전환

| 작업 | 대상 파일 | 내용 | 상태 |
|------|----------|------|------|
| EDK-01 | product.py → medicine.py | Coffee/Gummy → Medicine 클래스 교체 | 🔵 시작 |
| EDK-02 | kiosk_controller.py → drug_controller.py | 증상→의약품 매핑 로직으로 전환 | ⬜ 대기 |
| EDK-03 | data_manager.py | medicines.json / symptoms.json 데이터 구조 적용 | ⬜ 대기 |
| EDK-04 | main.py | 의약품 데이터 초기화 로직으로 교체 | ⬜ 대기 |
| EDK-05 | cli_view.py | 증상 선택 → 제품 탐색 → 결제 흐름으로 교체 | ⬜ 대기 |

### GUI 레이어 전환 (신규/수정)

| 작업 | 기존 파일 → 신규 파일 | 내용 | 상태 |
|------|-------------------|------|------|
| GUI-EDK-01 | main_window.py | 네비게이션 API를 EDK 화면 흐름으로 교체 | ⬜ 대기 |
| GUI-EDK-02 | main_menu.py → symptom_select.py | 증상 카테고리 선택 화면 | ⬜ 대기 |
| GUI-EDK-03 | product_list.py → medicine_list.py | 제품 목록 화면 | ⬜ 대기 |
| GUI-EDK-04 | customize.py → medicine_detail.py | 제품 상세 + 장바구니 담기 화면 | ⬜ 대기 |
| GUI-EDK-05 | (없음) → emergency.py | 응급 상황 안내 화면 (신규) | ⬜ 대기 |
| GUI-EDK-06 | admin_menu.py | 의약품 정보/재고 관리로 수정 | ⬜ 대기 |

---

## 목표 GUI 구조 (EDK 전환 후)

```
src/app/
├── main.py
├── drug_controller.py       # KioskController → DrugController
├── cli_view.py              # 증상 탐색 → 구매 → 결제 CLI 뷰
├── medicine.py              # Medicine 클래스 (Product 교체)
├── ingredient.py            # 재고 수량 (재활용)
├── cart.py                  # ✅ 재활용
├── payment.py               # ✅ 재활용
├── data_manager.py          # medicines.json / symptoms.json
├── exceptions.py            # ✅ 재활용
└── gui/
    ├── app.py               # ✅ 재활용
    ├── main_window.py       # 네비게이션 API 교체
    ├── voice_service.py     # ✅ 재활용
    └── screens/
        ├── idle.py              # ✅ 재활용
        ├── symptom_select.py    # 신규 (main_menu 교체)
        ├── medicine_list.py     # 신규 (product_list 교체)
        ├── medicine_detail.py   # 신규 (customize 교체)
        ├── cart.py              # ✅ 재활용
        ├── payment_method.py    # ✅ 재활용
        ├── cash_payment.py      # ✅ 재활용
        ├── receipt.py           # ✅ 재활용
        ├── emergency.py         # 신규 추가
        ├── admin_auth.py        # ✅ 재활용
        └── admin_menu.py        # 일부 수정
```

---

## 데이터 파일 구성 (EDK)

| 파일 | 내용 |
|------|------|
| `medicines.json` | 제품 목록 (이름, 효능, 복용법, 주의사항, 가격, 재고, 증상 카테고리) |
| `symptoms.json` | 증상 카테고리 정의 |
| `change_reserve.json` | 잔돈 보유량 (재활용) |
| `admin_config.json` | 관리자 비밀번호 (재활용) |

---

## Blocked Units

없음

---

## Current Risks

- 기존 테스트(test_*.py)가 구 도메인(커피/구미) 기반으로 작성되어 있어 전환 시 재작성 필요
- cart.py / payment.py 테스트는 로직 변경 없으면 그대로 재활용 가능

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
