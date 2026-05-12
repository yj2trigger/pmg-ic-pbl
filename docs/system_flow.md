# Micro-Factory Kiosk — 시스템 흐름 설계 (System Flow)

> 상태: 확정 (STEP 5 완료)

---

## 1. 전체 시스템 상태 머신

```
                    ┌─────────┐
               ┌───►│  IDLE   │◄──────────────────┐
               │    └────┬────┘                   │
               │         │ 상품 선택               │ 결제완료/취소
               │    ┌────▼──────────┐             │
               │    │   BROWSING    │             │
               │    └──┬─────────┬──┘             │
               │       │         │                │
               │  커피  │         │ 구미           │
               │  선택  │         │ 선택           │
          관리자│  ┌────▼───┐ ┌───▼──────┐        │
          모드  │  │CUSTOM  │ │ CUSTOM   │        │
          복귀  │  │_COFFEE │ │ _GUMMY   │        │
               │  └────┬───┘ └───┬──────┘        │
               │       └────┬────┘                │
               │       장바구니 추가               │
               │    ┌────▼──────────┐             │
               │    │ CART_VIEWING  │             │
               │    └────┬──────────┘             │
               │         │ 결제 진행              │
               │    ┌────▼──────────┐             │
               │    │PAYMENT_SELECT │             │
               │    └──┬─────────┬──┘             │
               │  현금 │         │ 카드            │
               │  ┌────▼───┐ ┌───▼──────────┐    │
               │  │ CASH_  │ │ CARD_PAYMENT │    │
               │  │PAYMENT │ └──────────────┘    │
               │  └────┬───┘        │            │
               │       └────────────┘            │
               │            │ 완료               │
               │    ┌────────▼───────┐           │
               │    │PAYMENT_COMPLETE├───────────┘
               │    └────────────────┘
               │
               │ 관리자 선택
          ┌────┴──────────┐
          │  ADMIN_AUTH   │
          └──────┬────────┘
                 │ 인증 성공
          ┌──────▼────────┐
          │  ADMIN_MODE   │
          └───────────────┘
```

### 상태 목록

| 상태 | 설명 |
|------|------|
| IDLE | 대기 화면 |
| BROWSING | 상품 선택 중 |
| CUSTOMIZING_COFFEE | 커피 커스텀 중 |
| CUSTOMIZING_GUMMY | 구미 커스텀 중 |
| CART_VIEWING | 장바구니 확인 중 |
| PAYMENT_SELECT | 결제 수단 선택 |
| CASH_PAYMENT | 현금 투입 중 |
| CARD_PAYMENT | 카드 결제 처리 중 |
| PAYMENT_COMPLETE | 결제 완료 |
| ADMIN_AUTH | 관리자 인증 중 |
| ADMIN_MODE | 관리자 모드 |

### 상태 전이 규칙

| 현재 상태 | 이벤트 | 다음 상태 |
|---------|--------|---------|
| IDLE | 상품 선택 | BROWSING |
| BROWSING | 커피 선택 | CUSTOMIZING_COFFEE |
| BROWSING | 구미 선택 | CUSTOMIZING_GUMMY |
| BROWSING | 관리자 선택 | ADMIN_AUTH |
| CUSTOMIZING_* | 장바구니 추가 | CART_VIEWING |
| CART_VIEWING | 결제 진행 | PAYMENT_SELECT |
| PAYMENT_SELECT | 현금 선택 | CASH_PAYMENT |
| PAYMENT_SELECT | 카드 선택 | CARD_PAYMENT |
| CASH_PAYMENT | 결제 성공 | PAYMENT_COMPLETE |
| CASH_PAYMENT | InsufficientChangeException | CART_VIEWING |
| CARD_PAYMENT | 결제 성공 | PAYMENT_COMPLETE |
| CARD_PAYMENT | PaymentException | PAYMENT_SELECT |
| PAYMENT_COMPLETE | 확인 | IDLE |
| ADMIN_AUTH | 인증 성공 | ADMIN_MODE |
| ADMIN_AUTH | 인증 실패 | BROWSING |
| ADMIN_MODE | 종료 | IDLE |

---

## 2. 메인 사용자 흐름

```
[시작]
  │
  ├─ 인기 상품 상위 N개 우선 표시 (통계 기반)
  ├─ 핫(🔥) 표시 원재료 포함 상품 배지 표시
  ├─ 품절 상품 → 선택 불가 표시
  │
  ▼
[메인 메뉴]
  1. 커피 주문
  2. 구미 주문
  3. 장바구니 보기
  4. 관리자 모드
  0. 종료
```

---

## 3. 커피 커스텀 흐름

```
[커피 커스텀]
  │
  Step 1. 종류 선택
  │       아메리카노 / 라떼 / 카푸치노
  │       → 종류에 따라 크림 옵션 활성화 여부 결정
  │
  Step 2. 크기 선택
  │       Small / Medium / Large
  │
  Step 3. 온도 선택
  │       HOT / ICE
  │
  Step 4. 당도/시럽 선택
  │       없음 / 보통 / 많이
  │
  Step 5. 샷 선택
  │       1샷 / 2샷
  │
  Step 6. 크림 선택 [라떼/카푸치노만 표시]
  │       있음 / 없음
  │
  Step 7. 수량 입력 (1 이상 정수)
  │
  Step 8. 현재 가격 표시
  │       base_price + Σoption_price × quantity
  │
  Step 9. 원재료 가용 여부 사전 확인
  │       → 부족 시 해당 옵션 선택 불가 처리
  │
  Step 10. 장바구니 추가 확인 → Cart에 OrderItem 추가
  │
  [메인 메뉴 복귀 또는 장바구니 이동]
```

---

## 4. 구미 커스텀 흐름

```
[구미 커스텀]
  │
  Step 1. 맛 선택
  │       딸기 / 포도 / 레몬
  │
  Step 2. 성분 선택
  │       비타민C / 오메가3 / 콜라겐
  │
  Step 3. 수량(알) 선택
  │       5알 / 10알 / 20알
  │
  Step 4. 패키지 선택
  │       낱개 / 파우치
  │
  Step 5. 구매 수량 입력 (1 이상 정수)
  │
  Step 6. 현재 가격 표시
  │
  Step 7. 원재료 가용 여부 사전 확인
  │
  Step 8. 장바구니 추가 확인
```

---

## 5. 장바구니 흐름

```
[장바구니]
  │
  ├─ 현재 담긴 항목 목록 표시
  │   번호 / 상품명 / 옵션 요약 / 수량 / 소계
  │
  ├─ 번들 할인 자동 계산 및 표시
  │   조건 충족 시 → 할인 금액 표시
  │
  ├─ 합계 표시 (할인 적용 후 final_amount)
  │
  선택:
  1. 항목 삭제
  2. 수량 변경
  3. 결제 진행  → [PAYMENT_SELECT]
  4. 계속 쇼핑 → [BROWSING]
  0. 장바구니 비우기
```

---

## 6. 현금 결제 흐름

```
[현금 결제]
  │
  현재 투입 금액: 0원 / 결제 금액: N원 표시
  │
  ┌─ 권종 선택 반복 ──────────────────────────┐
  │  1. 100원   2. 500원   3. 1,000원         │
  │  4. 5,000원 5. 10,000원  0. 취소          │
  │  → inserted_amount += 선택 권종           │
  │  → 투입 금액 / 결제 금액 / 잔액 갱신 표시  │
  └──────────────────────────────────────────┘
  │
  inserted_amount >= final_amount 시
  │
  [결제 확인] 선택
  │
  ├─ 잔돈 계산 (그리디 알고리즘)
  │   change_amount = inserted_amount - final_amount
  │   10000 → 5000 → 1000 → 500 → 100 순으로 차감
  │
  ├─ 잔돈 보유량 충분 여부 확인
  │   ├─ 충분 → 잔돈 반환 내역 출력
  │   │         재고 차감 → 통계 갱신 → JSON 저장
  │   │         결제 완료 화면
  │   │
  │   └─ 부족 → InsufficientChangeException
  │             투입 금액 전액 반환 내역 출력
  │             결제 취소 → [CART_VIEWING] 복귀
```

---

## 7. 카드 결제 흐름

```
[카드 결제]
  │
  결제 금액 확인 표시
  │
  [카드 결제 확인] 선택
  │
  try:
    카드 결제 시뮬레이션 (항상 성공)
    → 재고 차감 → 통계 갱신 → JSON 저장
    → 결제 완료 화면
  except PaymentException:
    → 결제 실패 메시지 출력
    → [PAYMENT_SELECT] 복귀
```

---

## 8. 잔돈 계산 알고리즘 (그리디)

```
change_breakdown = {}
remaining = change_amount

for denomination in [10000, 5000, 1000, 500, 100]:
    available = change_reserve[denomination]
    needed    = remaining // denomination
    use       = min(needed, available)

    if use > 0:
        change_breakdown[denomination] = use
        remaining -= use × denomination
        change_reserve[denomination] -= use

if remaining > 0:
    raise InsufficientChangeException
else:
    change_reserve 저장 → 반환 내역 출력
```

---

## 9. 재고 차감 흐름

```
결제 확정 시:
  │
  For each OrderItem in Cart:
    │
    레시피 조회 (상품 종류 + 선택된 옵션 조합)
    │
    For each ingredient in recipe:
      필요 수량 = recipe[ingredient] × item.quantity
      현재 재고 확인
      │
      ├─ 재고 충분 → ingredient.stock -= 필요 수량
      └─ 재고 부족 → InsufficientStockException
                     (UI 비활성화로 이 시점 도달 불가 → 방어 코드)
  │
  ingredients.json 저장
  │
  품절 상품 재확인 → UI 상태 갱신

재고 보충 시 (관리자):
  │
  원재료 선택 → 보충 수량 입력
  stock + 입력값 > max_capacity
    ├─ 초과 → StockOverflowException → 최대 보충 가능 수량 안내
    └─ 정상 → 재고 추가 → ingredients.json 저장
```

---

## 10. 관리자 흐름

```
[ADMIN_AUTH]
  비밀번호 입력
  │
  ├─ 일치 → [ADMIN_MODE]
  └─ 불일치 → AdminAuthException → 오류 메시지 → 재시도

[ADMIN_MODE 메뉴]
  1. 재고 관리       → 원재료 선택 → 보충 수량 입력
  2. 상품 관리       → 추가/삭제/ON-OFF → products.json 갱신
  3. 가격 관리       → 기본가/옵션 추가금 변경
  4. 매출 조회       → stats.json 읽기 → 표 출력
  5. 현금 보유량 관리 → change_reserve.json 읽기/수정
  6. 번들 할인 설정  → discount_policy.json 갱신
  7. 노출 설정       → top_n / hot_threshold → admin_config.json 갱신
  8. 비밀번호 변경   → admin_config.json 갱신
  9. 레시피 수정     → recipes.json 갱신 (형식 검증 후 저장)
  0. 종료           → [IDLE]
```

---

## 11. 통계 갱신 흐름

```
결제 완료 시:
  stats.json 읽기
  │
  sales[상품종류] += 구매수량
  ingredients_used[원재료] += 사용횟수
  revenue[total] += final_amount
  │
  stats.json 저장

핫(Hot) 표시 계산:
  total_orders = Σsales 전체 건수
  For each ingredient:
    ratio = ingredient_used[ingredient] / total_orders
    is_hot = ratio >= hot_threshold

인기 상품 계산:
  sales 정렬 (내림차순) → 상위 top_n개 우선 노출
```

---

## 12. 예외 흐름 전체 요약

| 예외 | 발생 위치 | 사용자 표시 | 복구 동작 |
|------|---------|-----------|---------|
| `StockOverflowException` | 관리자 재고 보충 | "최대 용량 초과. 최대 N개까지 가능" | 보충 취소, 메뉴 유지 |
| `InsufficientChangeException` | 현금 결제 잔돈 계산 | "잔돈 부족. N원 반환합니다" | 투입금 전액 반환, 장바구니 복귀 |
| `PaymentException` | 카드 결제 처리 | "결제 실패. 다시 시도해주세요" | 결제 수단 선택으로 복귀 |
| `InsufficientStockException` | 재고 차감 시 | 방어 코드 (정상 흐름에서 도달 불가) | 로그 기록 |
| `AdminAuthException` | 관리자 인증 | "비밀번호가 올바르지 않습니다" | 재입력 대기 |
| `InvalidRecipeException` | 레시피 JSON 로드 | "레시피 형식 오류. 변경 취소됨" | 이전 레시피 유지 |