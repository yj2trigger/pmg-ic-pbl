# Micro-Factory Kiosk — 용어 사전 (Terminology Dictionary)

> 상태: 확정 (STEP 3 완료)

---

## 1. 상품 도메인

| 한국어 용어 | 변수명 | 클래스명 | 시스템 내부 의미 | 사용자 화면 의미 |
|------------|--------|---------|--------------|--------------|
| 상품 | `product` | `Product` | 커피 또는 구미. 기본 가격 + 커스텀 옵션을 가지는 판매 단위 | 메인 화면 상품 선택 버튼 |
| 커피 | `coffee` | `Coffee(Product)` | Product 하위 타입. 종류/크기/온도/당도/샷/크림 옵션 보유 | "커피 주문하기" 버튼 |
| 영양 구미 | `gummy` | `Gummy(Product)` | Product 하위 타입. 맛/성분/수량/패키지 옵션 보유 | "구미 주문하기" 버튼 |
| 커스텀 옵션 | `option` | `CustomOption` | 사용자가 선택하는 속성 1개. 추가 금액 + 원재료 소비 정보 포함 | 선택 버튼 / 드롭다운 |
| 옵션 그룹 | `option_group` | `OptionGroup` | 관련 옵션들의 묶음 (예: 크기 그룹 = S/M/L) | 탭 또는 섹션으로 묶인 선택지 |
| 원재료 | `ingredient` | `Ingredient` | 상품 제조에 소비되는 단위 자원. 재고 관리의 기본 단위 | 미노출. 품절에 간접 영향 |
| 레시피 | `recipe` | `Recipe` | 커스텀 조합 → 소비 원재료 종류+수량 매핑. 관리자 JSON 설정 | 미노출 |

---

## 2. 커피 옵션 상세

| 옵션 그룹 | 선택지 | 변수명 | 특이사항 |
|----------|--------|--------|---------|
| 종류 | Americano / Latte / Cappuccino | `coffee_type` | 종류에 따라 크림 옵션 활성화 결정 |
| 크기 | Small / Medium / Large | `size` | 크기별 컵 원재료 구분 |
| 온도 | HOT / ICE | `temperature` | ICE 선택 시 얼음 원재료 소비 |
| 당도/시럽 | 없음 / 보통 / 많이 | `sweetness` | 시럽 원재료 소비량에 영향 |
| 샷 | 1샷 / 2샷 | `shot_count` | 원두 소비량에 영향 |
| 크림 | 있음 / 없음 | `has_cream` | 라떼, 카푸치노만 활성화 |

---

## 3. 구미 옵션 상세

| 옵션 그룹 | 선택지 | 변수명 | 특이사항 |
|----------|--------|--------|---------|
| 맛 | 딸기 / 포도 / 레몬 | `flavor` | 맛별 원재료(파우더) 구분 |
| 성분 | 비타민C / 오메가3 / 콜라겐 | `effect` | 성분별 원재료 구분 |
| 수량 | 5알 / 10알 / 20알 | `count` | 수량에 따라 원재료 소비 배수 |
| 패키지 | 낱개 / 파우치 | `package_type` | 패키지 원재료 구분 |

---

## 4. 가격 도메인

| 한국어 용어 | 변수명 | 타입 | 정의 |
|------------|--------|------|------|
| 기본 가격 | `base_price` | `int` | 옵션 미선택 상태의 상품 가격 (원 단위) |
| 옵션 추가 금액 | `option_price` | `int` | 커스텀 옵션 1개 선택 시 추가 금액 |
| 최종 가격 | `total_price` | `int` | base_price + Σoption_price |
| 번들 할인 | `bundle_discount` | `BundleDiscount` | 조건 충족 시 최종 가격에서 차감. 관리자 JSON 정의 |
| 할인 정책 | `discount_policy` | `DiscountPolicy` | 번들 조건 + 할인율/금액 규칙 집합 |
| 결제 금액 | `final_amount` | `int` | 번들 할인 적용 후 실제 청구 금액 |

---

## 5. 재고 도메인

| 한국어 용어 | 변수명 | 정의 | 경계 조건 |
|------------|--------|------|---------|
| 재고 | `stock` | 원재료의 현재 보유 수량 | 0 ≤ stock ≤ max_capacity |
| 최대 용량 | `max_capacity` | 원재료별 최대 보유 가능 수량. 관리자 설정 | 초과 입력 시 StockOverflowException |
| 품절 | `out_of_stock` | 레시피 수행에 필요한 원재료 중 하나라도 재고 부족인 상태 | 해당 상품 옵션 비활성화 트리거 |
| 비활성화 | `disabled` | 품절 상태의 상품/옵션이 UI에서 선택 불가 처리된 상태 | 버튼 state=DISABLED |

---

## 6. 장바구니 / 주문 도메인

| 한국어 용어 | 변수명 | 클래스명 | 정의 |
|------------|--------|---------|------|
| 장바구니 | `cart` | `Cart` | 결제 전 사용자가 담은 주문 항목 목록 |
| 주문 항목 | `order_item` | `OrderItem` | 상품 1종 + 선택된 옵션 조합 + 수량 + 소계 금액 |
| 수량 | `quantity` | `int` | 동일 커스텀 조합의 구매 개수 (≥ 1) |
| 소계 | `subtotal` | `int` | total_price × quantity |
| 장바구니 합계 | `cart_total` | `int` | Σsubtotal (번들 할인 적용 전) |
| 결제 금액 | `final_amount` | `int` | 번들 할인 적용 후 최종 청구 금액 |

---

## 7. 결제 도메인

| 한국어 용어 | 변수명 | 클래스명 | 정의 |
|------------|--------|---------|------|
| 결제 | `payment` | `Payment` | 장바구니 확정 후 금액 지불 행위 전체 |
| 현금 결제 | `cash_payment` | `CashPayment(Payment)` | 권종별 누적 투입 방식의 결제 |
| 카드 결제 | `card_payment` | `CardPayment(Payment)` | 버튼 클릭 즉시 성공 처리 시뮬레이션 |
| 권종 | `denomination` | `Denomination` (Enum) | 100 / 500 / 1000 / 5000 / 10000원 |
| 누적 투입 금액 | `inserted_amount` | `int` | 현금 결제 중 누적된 투입 금액 합계 |
| 잔돈 | `change_amount` | `int` | inserted_amount - final_amount |
| 잔돈 보유량 | `change_reserve` | `ChangeReserve` | 키오스크 내 각 권종의 보유 수량 |
| 잔돈 반환 내역 | `change_breakdown` | `dict[Denomination, int]` | 반환할 권종별 수량 (그리디 알고리즘 결과) |

---

## 8. 관리자 도메인

| 한국어 용어 | 변수명 | 정의 |
|------------|--------|------|
| 관리자 | `admin` | 키오스크 설정/재고/통계에 접근 가능한 권한자 |
| 관리자 비밀번호 | `admin_password` | JSON에 저장. 관리자가 변경 가능 |
| 관리자 인증 | `admin_auth` | 비밀번호 입력 검증 절차 |
| 매출 | `revenue` | 결제 완료된 final_amount의 누적 합산 |
| 현금 보유량 | `cash_reserve` | 키오스크 내 권종별 현금 수량 (잔돈 보유량과 동일 관리) |
| 판매 통계 | `sales_stats` | 상품(커피/구미)별 판매 건수. stats.json 누적 |
| 원재료 사용 통계 | `ingredient_stats` | 원재료별 소비 횟수. stats.json 누적 |
| 핫(Hot) 표시 | `is_hot` | 전체 주문 대비 특정 원재료 사용 비율이 임계값 초과 시 표시 |
| 핫 임계값 | `hot_threshold` | 관리자가 설정하는 핫 표시 기준 비율 (예: 30%) |
| 인기 상품 | `popular_product` | 판매 건수 기준 상위 N개 상품 |
| 우선 노출 N | `top_n` | 관리자가 설정하는 우선 노출 상품 수 |
| 판매 상품 | `available_products` | 현재 키오스크에서 판매 중인 상품 목록. 관리자 ON/OFF |

---

## 9. 예외 도메인

| 예외 클래스명 | 발생 조건 | 처리 방식 |
|-------------|---------|---------|
| `StockOverflowException` | 재고 보충 시 max_capacity 초과 입력 | 관리자 화면에 오류 메시지, 보충 취소 |
| `InsufficientChangeException` | 잔돈 반환 불가 (보유 권종 부족) | 결제 중단, 투입 금액 전액 반환 |
| `PaymentException` | 결제 처리 실패 | 결제 취소, 사용자 알림 메시지 |
| `InsufficientStockException` | 레시피 실행 시 원재료 부족 | UI 비활성화로 선제 방지 |
| `AdminAuthException` | 관리자 비밀번호 불일치 | 접근 거부 메시지 |
| `InvalidRecipeException` | 레시피 JSON 형식 오류 | 로드 실패 알림, 이전 레시피 유지 |

---

## 10. JSON 파일 구조 (확정 8개)

| 파일명 | 역할 | 갱신 시점 |
|--------|------|---------|
| `products.json` | 상품 목록, 기본 가격, 판매 ON/OFF | 관리자 수정 시 |
| `ingredients.json` | 원재료 목록, 현재 재고, 최대 용량 | 구매 완료 / 관리자 보충 시 |
| `recipes.json` | 상품-옵션 조합 → 원재료 소비량 매핑 | 관리자 수정 시 |
| `options.json` | 옵션 그룹, 선택지, 추가 금액 | 관리자 수정 시 |
| `change_reserve.json` | 키오스크 내 권종별 현금 보유량 | 결제 완료 / 관리자 수정 시 |
| `stats.json` | 상품별 판매 건수 + 원재료 사용 횟수 + 매출 누적 | 결제 완료 시 |
| `discount_policy.json` | 번들 할인 조건 및 할인율 | 관리자 수정 시 |
| `admin_config.json` | 관리자 비밀번호, top_n, hot_threshold | 관리자 수정 시 |