# Micro-Factory Kiosk — 테스트 전략 (Test Strategy)

> 상태: 확정 (STEP 7 완료)

---

## 1. 테스트 파일 구조

```
tests/
├── test_exceptions.py     # KioskException 계층 단위 테스트
├── test_ingredient.py     # Ingredient 단위 테스트
├── test_recipe.py         # Recipe 단위 테스트
├── test_product.py        # Product, CustomOption, OptionGroup 테스트
├── test_cart.py           # Cart, OrderItem 테스트
├── test_payment.py        # Payment, CashPayment, CardPayment, ChangeReserve 테스트
├── test_discount.py       # DiscountPolicy, BundleDiscount 테스트
├── test_stats.py          # Statistics 테스트
├── test_data_manager.py   # DataManager JSON I/O 테스트
└── test_controller.py     # KioskController 통합 테스트
```

---

## 2. 테스트 분류 기준

| 분류 | 대상 | 이유 |
|------|------|------|
| 단위 테스트 | Ingredient, Cart, ChangeReserve, DiscountPolicy, Statistics | 외부 의존 없음. mock 불필요 |
| 경계값 테스트 | 재고 0/max, 잔돈 0, 수량 1, 할인 조건 경계 | 감점 주요 원인. 반드시 검증 |
| 예외 테스트 | 6개 예외 클래스 전부 | 과제 요구사항: "예외 없어야 함" → 처리 검증 |
| 통합 테스트 | KioskController | 결제→재고차감→통계 흐름 전체 검증 |
| I/O 테스트 | DataManager | JSON 저장/로드 정합성 검증 |

---

## 3. test_ingredient.py — TestIngredient

| 테스트 메서드 | 시나리오 | 검증 내용 | 분류 |
|-------------|---------|---------|------|
| test_deduct_normal | stock=100, deduct(30) | stock == 70 | 단위 |
| test_deduct_exact | stock=50, deduct(50) | stock == 0 | 경계값 |
| test_deduct_insufficient | stock=30, deduct(31) | InsufficientStockException | 예외 |
| test_deduct_zero | stock=50, deduct(0) | stock == 50 | 경계값 |
| test_replenish_normal | stock=50, max=100, replenish(30) | stock == 80 | 단위 |
| test_replenish_to_max | stock=90, max=100, replenish(10) | stock == 100 | 경계값 |
| test_replenish_overflow | stock=90, max=100, replenish(11) | StockOverflowException | 예외 |
| test_is_available_true | stock=50, needed=50 | True | 경계값 |
| test_is_available_false | stock=50, needed=51 | False | 경계값 |
| test_is_out_of_stock_true | stock=0 | True | 경계값 |
| test_is_out_of_stock_false | stock=1 | False | 경계값 |
| test_remaining_capacity | stock=30, max=100 | remaining == 70 | 단위 |

---

## 4. test_recipe.py — TestRecipe

| 테스트 메서드 | 시나리오 | 검증 내용 | 분류 |
|-------------|---------|---------|------|
| test_get_required_single_option | 옵션 1개 선택 | 원재료 소비량 정확 | 단위 |
| test_get_required_multiple_options | 옵션 3개 선택 | 원재료 소비량 합산 정확 | 단위 |
| test_get_required_no_options | 옵션 없음 | 빈 dict 반환 | 경계값 |
| test_can_fulfill_all_available | 모든 원재료 충분 | True | 단위 |
| test_can_fulfill_one_short | 원재료 1종 부족 | False | 단위 |
| test_can_fulfill_exact_stock | 필요량 = 재고량 정확히 일치 | True | 경계값 |
| test_can_fulfill_empty_options | 선택 옵션 없음 | True (소비 없음) | 경계값 |

---

## 5. test_product.py — TestProduct, TestCustomOption, TestOptionGroup

| 테스트 메서드 | 시나리오 | 검증 내용 | 분류 |
|-------------|---------|---------|------|
| test_calculate_price_no_options | 옵션 미선택 | base_price 그대로 반환 | 단위 |
| test_calculate_price_with_options | 옵션 2개 선택 | base + option1 + option2 | 단위 |
| test_cream_active_for_latte | 라떼 상품 | is_active_for == True | 단위 |
| test_cream_inactive_for_americano | 아메리카노 상품 | is_active_for == False | 단위 |
| test_option_extra_price | extra_price=500 | get_extra_price() == 500 | 단위 |

---

## 6. test_cart.py — TestOrderItem, TestCart

| 테스트 메서드 | 시나리오 | 검증 내용 | 분류 |
|-------------|---------|---------|------|
| test_order_item_subtotal | price=3500, qty=2 | subtotal == 7000 | 단위 |
| test_order_item_subtotal_qty_one | price=3500, qty=1 | subtotal == 3500 | 경계값 |
| test_cart_add_item | 항목 1개 추가 | items 길이 == 1 | 단위 |
| test_cart_add_multiple | 항목 3개 추가 | items 길이 == 3 | 단위 |
| test_cart_remove_item | 항목 2개 중 0번 삭제 | items 길이 == 1, 올바른 항목 잔존 | 단위 |
| test_cart_get_subtotal | 항목 2개, 각 소계 3000/5000 | subtotal == 8000 | 단위 |
| test_cart_get_subtotal_empty | 빈 장바구니 | subtotal == 0 | 경계값 |
| test_cart_is_empty_true | 항목 없음 | True | 단위 |
| test_cart_is_empty_false | 항목 1개 | False | 단위 |
| test_cart_clear | 항목 3개 후 clear() | items == [] | 단위 |
| test_cart_update_quantity | qty 2 → 5 | subtotal 변화 반영 | 단위 |

---

## 7. test_payment.py — TestChangeReserve, TestCashPayment, TestCardPayment

| 테스트 메서드 | 시나리오 | 검증 내용 | 분류 |
|-------------|---------|---------|------|
| test_dispense_normal | change=1600, reserve 충분 | {1000:1, 500:1, 100:1} | 단위 |
| test_dispense_exact_denomination | change=5000, 5000원 1개 보유 | {5000:1} | 단위 |
| test_dispense_no_large_use_small | change=1000, 1000원 0개/500원 5개 | {500:2} | 경계값 |
| test_dispense_zero_change | change=0 | 빈 dict, reserve 변화 없음 | 경계값 |
| test_dispense_insufficient | change=500, 100원 3개만 보유 | InsufficientChangeException | 예외 |
| test_dispense_updates_reserve | 잔돈 반환 후 | reserve에서 해당 권종 차감 확인 | 단위 |
| test_can_make_change_true | 반환 가능한 reserve | True | 단위 |
| test_can_make_change_false | 반환 불가 | False | 단위 |
| test_cash_insert_accumulates | 1000+500+100 투입 | inserted_amount == 1600 | 단위 |
| test_cash_can_complete_true | inserted=5000, amount=4500 | True | 단위 |
| test_cash_can_complete_false | inserted=3000, amount=4500 | False | 단위 |
| test_cash_can_complete_exact | inserted=4500, amount=4500 | True | 경계값 |
| test_cash_get_change_amount | inserted=5000, amount=4500 | 500 | 단위 |
| test_cash_get_change_zero | inserted=amount | 0 | 경계값 |
| test_cash_process_success | 정상 결제 | 잔돈 내역 dict 반환 | 단위 |
| test_cash_process_insufficient_change | 잔돈 부족 | InsufficientChangeException | 예외 |
| test_card_process_success | 카드 결제 | True 반환 | 단위 |

---

## 8. test_discount.py — TestBundleDiscount, TestDiscountPolicy

| 테스트 메서드 | 시나리오 | 검증 내용 | 분류 |
|-------------|---------|---------|------|
| test_bundle_applicable | item_count=2, 조건=2이상 | is_applicable == True | 단위 |
| test_bundle_not_applicable | item_count=1, 조건=2이상 | is_applicable == False | 단위 |
| test_bundle_exact_condition | item_count=2, 조건=2 | True | 경계값 |
| test_bundle_calculate_rate | subtotal=10000, rate=10% | calculate == 1000 | 단위 |
| test_bundle_calculate_amount | 고정 금액 할인 500원 | calculate == 500 | 단위 |
| test_policy_no_rules | 규칙 없음 | apply == 0 | 경계값 |
| test_policy_one_rule_applies | 규칙 1개 충족 | 할인 금액 반환 | 단위 |
| test_policy_multiple_rules_max | 규칙 2개 모두 충족 | 최대 할인액 반환 | 단위 |
| test_policy_rule_not_applicable | 조건 미충족 | apply == 0 | 단위 |

---

## 9. test_stats.py — TestStatistics

| 테스트 메서드 | 시나리오 | 검증 내용 | 분류 |
|-------------|---------|---------|------|
| test_record_sales_increment | 커피 1개 구매 | sales['coffee'] == 1 | 단위 |
| test_record_revenue_increment | 결제 금액 4500 | revenue == 4500 | 단위 |
| test_record_ingredient_increment | 원두 1 소비 | ingredients_used['coffee_bean'] == 1 | 단위 |
| test_record_multiple | 구매 3회 | 각 카운트 누적 정확 | 단위 |
| test_get_popular_order | 커피3/구미1 | 커피 먼저 반환 | 단위 |
| test_get_popular_n_limit | 상품 5개, n=2 | 길이 == 2 | 단위 |
| test_get_popular_n_exceeds | 상품 2개, n=5 | 길이 == 2 (전체 반환) | 경계값 |
| test_hot_above_threshold | 원두 40%, threshold=30% | 원두 포함 | 단위 |
| test_hot_below_threshold | 원두 20%, threshold=30% | 원두 미포함 | 단위 |
| test_hot_exact_threshold | 비율 = threshold | 포함 (≥ 기준) | 경계값 |
| test_hot_no_orders | 주문 0건 | ZeroDivisionError 없이 빈 리스트 | 경계값 |
| test_serialization_roundtrip | to_dict() → from_dict() | 원본과 동일 | 단위 |

---

## 10. test_data_manager.py — TestDataManager

| 테스트 메서드 | 시나리오 | 검증 내용 | 분류 |
|-------------|---------|---------|------|
| test_save_load_products | 저장 후 로드 | 원본 데이터와 동일 | I/O |
| test_save_load_ingredients | 저장 후 로드 | 원본 데이터와 동일 | I/O |
| test_save_load_stats | 저장 후 로드 | 원본 데이터와 동일 | I/O |
| test_save_load_change_reserve | 저장 후 로드 | 원본 데이터와 동일 | I/O |
| test_invalid_recipe_json | 잘못된 형식 JSON | InvalidRecipeException 발생 | 예외 |
| test_missing_file_handled | 파일 없을 때 로드 | 예외 없이 기본값 반환 | 예외 |

> tempfile.mkdtemp()를 사용하여 실제 data/ 파일 오염 방지

---

## 11. test_controller.py — TestKioskController

| 테스트 메서드 | 시나리오 | 검증 내용 | 분류 |
|-------------|---------|---------|------|
| test_add_to_cart_success | 정상 상품+옵션 추가 | cart.is_empty() == False | 통합 |
| test_get_final_amount_with_discount | 할인 적용 | final_amount < subtotal | 통합 |
| test_get_final_amount_no_discount | 할인 미적용 | final_amount == subtotal | 통합 |
| test_cash_payment_deducts_stock | 결제 완료 후 | 원재료 stock 감소 확인 | 통합 |
| test_cash_payment_updates_stats | 결제 완료 후 | stats.revenue 증가 확인 | 통합 |
| test_cash_payment_clears_cart | 결제 완료 후 | cart.is_empty() == True | 통합 |
| test_admin_auth_correct | 올바른 비밀번호 | True 반환 | 통합 |
| test_admin_auth_wrong | 틀린 비밀번호 | AdminAuthException | 예외 |
| test_admin_replenish_success | 정상 보충 | stock 증가 확인 | 통합 |
| test_admin_replenish_overflow | 초과 보충 | StockOverflowException | 예외 |
| test_insufficient_change_returns_to_cart | 잔돈 부족 결제 | cart 유지, inserted_amount 반환 | 통합 |

---

## 12. 경계값 우선순위

| 우선순위 | 경계값 | 이유 |
|---------|--------|------|
| 🔴 최우선 | stock = 0 (품절) | 시나리오 필수 요구사항 |
| 🔴 최우선 | stock = max_capacity (정확히 가득) | StockOverflowException 경계 |
| 🔴 최우선 | inserted_amount = final_amount (잔돈 0원) | InsufficientChangeException 방지 |
| 🟡 중요 | change = 0 (잔돈 없음) | 빈 dict 반환 처리 |
| 🟡 중요 | 빈 cart에서 결제 시도 | 예외 또는 차단 처리 |
| 🟡 중요 | quantity = 1 (최소 수량) | OrderItem 최솟값 |
| 🟢 보통 | Statistics: 주문 0건에서 hot 계산 | ZeroDivisionError 방지 |
| 🟢 보통 | get_popular(n) n이 상품 수 초과 | IndexError 방지 |

---

## 13. 예외 검증 체크리스트

| 예외 클래스 | 테스트 파일 | 테스트 메서드 | 검증 방법 |
|------------|-----------|------------|---------|
| StockOverflowException | test_ingredient.py | test_replenish_overflow | assertRaises |
| InsufficientStockException | test_ingredient.py | test_deduct_insufficient | assertRaises |
| InsufficientChangeException | test_payment.py | test_dispense_insufficient | assertRaises |
| PaymentException | test_payment.py | test_card_process_success | try/except 처리 확인 |
| AdminAuthException | test_controller.py | test_admin_auth_wrong | assertRaises |
| InvalidRecipeException | test_data_manager.py | test_invalid_recipe_json | assertRaises |

---

## 14. 테스트 작성 규칙

1. 테스트 클래스: unittest.TestCase 상속
2. 준비 코드: setUp() 메서드에서 공통 객체 초기화
3. 정리 코드: tearDown() 메서드에서 임시 파일 삭제 (DataManager만)
4. 메서드 이름: test_[대상]_[시나리오] 형태
5. 단언: assertEqual, assertTrue, assertFalse, assertRaises 사용
6. 독립성: 각 테스트는 다른 테스트에 의존하지 않음
7. mock 사용: KioskController 테스트에서만 DataManager mock 허용