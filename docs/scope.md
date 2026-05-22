# EDK (Erica Drug King) — 구현 범위 확정 (Scope)

> 상태: 실제 판매 방식 반영 (2026-05-23)

---

## 1. 레이어 구조

```
┌──────────────────────────────────────────────────────┐
│              Business Logic Layer                    │
│  (Medicine / SymptomGroup / Cart / Payment / ...)    │
│  → View가 무엇인지 절대 모름                           │
│  → optional logger 콜백만 수신                        │
└─────────────┬────────────────────────────────────────┘
              │ 함수 호출
    ┌─────────┴──────────┐
    │                    │
┌───▼──────┐     ┌───────▼──────────────┐
│ CLI View │     │ GUI View (PyQt6)     │
│(제출용)  │     │+ CLI Logger (시연용)  │
│ 터미널   │     │ GUI 클릭 → 터미널 출력 │
└──────────┘     └──────────────────────┘
```

---

## 2. 구현 Phase 계획

| Phase | 내용 | 상태 |
|-------|------|------|
| Phase 1 | Medicine / SymptomGroup / Symptom (기존 Product/OptionGroup 교체) | 🔄 전환 필요 |
| Phase 2 | Cart / Payment / ChangeReserve — **그대로 재활용** | ✅ 재활용 |
| Phase 3 | JSON 영속성 (의약품 데이터) | 🔄 전환 필요 |
| Phase 4 | CLI View (터미널 단독 동작) | 🔄 전환 필요 |
| Phase 5 | GUI View 교체 (기존 PyQt6 재활용) | 🔄 화면 교체 필요 |
| Phase 6 | 관리자 기능 (의약품 정보/재고/결제 관리) | 🔄 전환 필요 |

---

## 3. 반드시 구현할 기능 (Must-Have)

| # | 기능 | 설명 |
|---|------|------|
| 1 | 증상 카테고리 선택 | 두통/감기/소화불량/피로/외상 등 |
| 2 | 제품 추천 목록 표시 | 증상에 해당하는 판매 가능 제품 목록 |
| 3 | 제품 상세 정보 | 효능, 복용법, 주의사항, 가격, 재고 표시 |
| 4 | 장바구니 | 여러 제품 담기, 수량 변경, 재고 연동 |
| 5 | 현금 결제 | 누적 투입 + 잔돈 반환 (100/500/1000/5000/10000원) |
| 6 | 카드 결제 | 시뮬레이션 처리 |
| 7 | 재고 소진 처리 | 품절 시 선택 불가 표시 |
| 8 | 응급 상황 분기 | 응급 증상 감지 시 병원 방문 안내 화면 |
| 9 | JSON 영속성 | 제품 데이터, 재고, 잔돈 보유량 JSON 관리 |
| 10 | 관리자 모드 | 비밀번호 인증, 제품/재고/가격/현금 관리 |
| 11 | 예외 처리 | 잔돈 부족, 재고 부족, 데이터 오류 등 |

---

## 4. 기존 코드 재활용 전략

| 기존 구성요소 | 재활용 방식 |
|-------------|-----------|
| `Product` → `Medicine` | product_type → symptom_category로 교체 |
| `OptionGroup` → `SymptomGroup` | 증상 카테고리 그룹 |
| `CustomOption` → `Symptom` | 개별 증상 항목 |
| `Ingredient` | 의약품/영양제 재고 수량으로 그대로 재활용 |
| `Cart` | **그대로 재활용** (실제 판매이므로 장바구니 필요) |
| `Payment` (CashPayment, CardPayment) | **그대로 재활용** |
| `ChangeReserve` | **그대로 재활용** |
| `KioskController` | DrugController로 리팩터링 |
| `DataManager` | 의약품 JSON 데이터 관리로 재활용 |
| `gui/main_window.py` | 화면 스택 구조 그대로, 네비게이션 API 수정 |
| `gui/voice_service.py` | 그대로 재활용 |
| `gui/screens/admin_auth.py` | 그대로 재활용 |
| `gui/screens/cart.py` | **그대로 재활용** |
| `gui/screens/payment_method.py` | **그대로 재활용** |
| `gui/screens/cash_payment.py` | **그대로 재활용** |
| `gui/screens/receipt.py` | 영수증 화면 — **그대로 재활용** |

---

## 5. 신규/수정 GUI 화면 구성

| 화면 | 파일 | 처리 방식 |
|------|------|----------|
| 대기 화면 | `screens/idle.py` | 재활용 |
| 증상 선택 화면 | `screens/symptom_select.py` | main_menu.py 교체 (신규) |
| 제품 목록 화면 | `screens/medicine_list.py` | product_list.py 교체 (신규) |
| 제품 상세 화면 | `screens/medicine_detail.py` | customize.py 교체 (신규) |
| 장바구니 화면 | `screens/cart.py` | **재활용** |
| 결제 수단 선택 | `screens/payment_method.py` | **재활용** |
| 현금 결제 화면 | `screens/cash_payment.py` | **재활용** |
| 영수증 화면 | `screens/receipt.py` | **재활용** |
| 응급 안내 화면 | `screens/emergency.py` | 신규 추가 |
| 관리자 인증 화면 | `screens/admin_auth.py` | 재활용 |
| 관리자 메뉴 화면 | `screens/admin_menu.py` | 일부 수정 (의약품 관리로) |

---

## 6. 제외 범위

| 항목 | 이유 |
|------|------|
| 전문의약품 / 처방약 | 무허가 판매 불가 |
| 실제 카드 결제 API | 시뮬레이션 대체 |
| 네트워크 통신 / 서버 | 로컬 단독 실행 |
| DB (SQLite 등) | JSON 대체 |
| 번들 할인 정책 | 후순위 (필요 시 추가) |

---

## 7. 데이터 파일 구성

| 파일 | 내용 |
|------|------|
| `medicines.json` | 제품 목록 (이름, 효능, 복용법, 주의사항, 가격, 재고, 증상 카테고리) |
| `symptoms.json` | 증상 카테고리 정의 |
| `change_reserve.json` | 잔돈 보유량 (재활용) |
| `admin_config.json` | 관리자 비밀번호 (재활용) |
