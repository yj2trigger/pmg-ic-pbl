# EDK (Erica Drug King) — 구현 범위 확정 (Scope)

> 상태: 도메인 전환 반영 (2026-05-23)

---

## 1. 레이어 구조

```
┌─────────────────────────────────────────────────┐
│           Business Logic Layer                  │
│  (Medicine / SymptomGroup / MedicineInfo / ...)  │
│  → View가 무엇인지 절대 모름                      │
│  → optional logger 콜백만 수신                   │
└─────────────┬───────────────────────────────────┘
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
| Phase 2 | MedicineInfo / 주의사항 데이터 구조 | 🔄 신규 구현 필요 |
| Phase 3 | JSON 영속성 (의약품 데이터) | 🔄 전환 필요 |
| Phase 4 | CLI View (터미널 단독 동작) | 🔄 전환 필요 |
| Phase 5 | GUI View 교체 (기존 PyQt6 재활용) | 🔄 화면 교체 필요 |
| Phase 6 | 관리자 기능 (의약품 정보 관리) | 🔄 전환 필요 |

---

## 3. 반드시 구현할 기능 (Must-Have)

| # | 기능 | 설명 |
|---|------|------|
| 1 | 증상 카테고리 선택 | 두통/감기/소화불량/피로/외상 등 |
| 2 | 의약품 추천 목록 표시 | 증상에 해당하는 의약품 리스트 |
| 3 | 의약품 상세 정보 | 효능, 복용법, 주의사항 표시 |
| 4 | 응급 상황 분기 | 응급 증상 감지 시 병원 방문 안내 화면 |
| 5 | JSON 영속성 | 의약품 데이터 JSON 파일 관리 |
| 6 | 관리자 모드 | 비밀번호 인증, 의약품 정보/재고 관리 |
| 7 | 예외 처리 | 데이터 오류, 잘못된 입력 등 처리 |
| 8 | 재고 수량 표시 | 의약품 재고 부족 시 사용자 안내 |

---

## 4. 기존 코드 재활용 전략

| 기존 구성요소 | 재활용 방식 |
|-------------|-----------|
| `Product` → `Medicine` | product_type → symptom_type으로 교체 |
| `OptionGroup` → `SymptomGroup` | 증상 카테고리 그룹 |
| `CustomOption` → `Symptom` | 개별 증상 항목 |
| `Ingredient` | 의약품 재고 수량으로 그대로 재활용 |
| `Cart` | 관심 의약품 선택 목록 (결제 없음) |
| `Payment` | 제거 (정보 제공 서비스, 결제 불필요) |
| `KioskController` | DrugController로 리팩터링 |
| `DataManager` | 의약품 JSON 데이터 관리로 재활용 |
| `gui/main_window.py` | 화면 스택 구조 그대로 재활용 |
| `gui/screens/` | EDK 화면 흐름에 맞게 교체 |
| `gui/voice_service.py` | TTS 음성 안내 그대로 재활용 |

---

## 5. 신규 GUI 화면 구성

| 화면 | 파일 | 기존 대응 |
|------|------|----------|
| 대기 화면 | `screens/idle.py` | 재활용 |
| 증상 선택 화면 | `screens/symptom_select.py` | main_menu.py 교체 |
| 의약품 목록 화면 | `screens/medicine_list.py` | product_list.py 교체 |
| 의약품 상세 화면 | `screens/medicine_detail.py` | customize.py 교체 |
| 주의사항 화면 | `screens/caution.py` | receipt.py 교체 |
| 응급 안내 화면 | `screens/emergency.py` | 신규 추가 |
| 관리자 인증 화면 | `screens/admin_auth.py` | 재활용 |
| 관리자 메뉴 화면 | `screens/admin_menu.py` | 일부 수정 |

---

## 6. 제외 범위

| 항목 | 이유 |
|------|------|
| 결제 시스템 (현금/카드) | 정보 제공 서비스 — 판매 없음 |
| 장바구니 결제 흐름 | 불필요 |
| 번들 할인 정책 | 불필요 |
| 실제 카드 결제 API | 불필요 |
| 네트워크 통신 / 서버 | 로컬 단독 실행 |
| DB (SQLite 등) | JSON 대체 |

---

## 7. 데이터 파일 구성

| 파일 | 내용 |
|------|------|
| `medicines.json` | 의약품 목록 (이름, 효능, 복용법, 주의사항, 재고) |
| `symptoms.json` | 증상 카테고리 및 매핑 데이터 |
| `admin_config.json` | 관리자 비밀번호 |
