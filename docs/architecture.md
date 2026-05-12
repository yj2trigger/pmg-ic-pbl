# Micro-Factory Kiosk — 아키텍처 초안 (Architecture)

> 상태: 확정 (STEP 6 완료)

---

## 1. 파일 구조

```
project/
├── src/
│   └── app/
│       ├── main.py              # 진입점 — 의존성 생성 및 연결
│       ├── exceptions.py        # 커스텀 예외 6종
│       │
│       ├── product.py           # Product, Coffee, Gummy, CustomOption, OptionGroup
│       ├── ingredient.py        # Ingredient
│       ├── cart.py              # Cart, OrderItem (재고 확인 포함)
│       ├── payment.py           # Payment, CashPayment, CardPayment, ChangeReserve
│       ├── discount.py          # DiscountPolicy, BundleDiscount
│       ├── stats.py             # Statistics
│       │
│       ├── data_manager.py      # DataManager — JSON 읽기/쓰기 전담
│       ├── kiosk_controller.py  # KioskController — 비즈니스 로직 조율
│       ├── cli_view.py          # CLIView — 터미널 인터페이스
│       │
│       └── data/
│           ├── products.json
│           ├── ingredients.json
│           ├── recipes.json
│           ├── options.json
│           ├── change_reserve.json
│           ├── stats.json
│           ├── discount_policy.json
│           └── admin_config.json
├── tests/
│   ├── test_exceptions.py
│   ├── test_ingredient.py
│   ├── test_product.py
│   ├── test_cart.py
│   ├── test_payment.py
│   ├── test_discount.py
│   ├── test_stats.py
│   ├── test_data_manager.py
│   └── test_controller.py
├── assets/
│   └── icon.png
├── pyproject.toml        # 패키징 설정
└── README.md             # 빌드 방법
```

---

## 2. 의존성 방향

```
exceptions.py
    ↑ (모든 파일이 import)

product.py    ingredient.py    payment.py    stats.py
    ↑               ↑               ↑            ↑
    └───────────── cart.py      discount.py      │
                    ↑               ↑            │
                    └───────── data_manager.py ──┘
                                    ↑
                           kiosk_controller.py
                                    ↑
                              cli_view.py
                                    ↑
                                main.py
```

**핵심 규칙:**
- 하위 모듈은 상위 모듈을 절대 import하지 않는다
- `cli_view.py`는 `kiosk_controller.py`만 안다 — 모델 클래스 직접 접근 금지
- `Cart`는 할인 로직 미포함 — 순환 의존 방지, Controller에서 처리

---

## 3. 클래스 책임 정의

### exceptions.py

| 클래스 | 발생 조건 |
|--------|---------|
| `KioskException` | 모든 키오스크 예외의 공통 base |
| `StockOverflowException` | 재고 보충 시 max_capacity 초과 |
| `InsufficientChangeException` | 잔돈 보유량 부족 |
| `PaymentException` | 결제 처리 실패 |
| `InsufficientStockException` | 결제 시 원재료 부족 (방어용) |
| `AdminAuthException` | 관리자 비밀번호 불일치 |
| `InvalidRecipeException` | 레시피 JSON 형식 오류 |

---

### product.py

**`CustomOption`** — 선택 가능한 옵션 1개

| 속성/메서드 | 설명 |
|-----------|------|
| `option_id`, `name`, `extra_price` | 식별자, 표시명, 추가 금액 |
| `get_extra_price() → int` | 추가 금액 반환 |

**`OptionGroup`** — 옵션 묶음 (예: 크기 그룹 = S/M/L)

| 속성/메서드 | 설명 |
|-----------|------|
| `group_id`, `name`, `options`, `active_for` | 식별자, 이름, 옵션 목록, 활성화 대상 상품 타입 |
| `is_active_for(product_type) → bool` | 해당 상품에 이 그룹이 적용되는지 |
| `get_options() → list[CustomOption]` | 포함된 옵션 목록 반환 |

**`Product`** (base) — 판매 상품의 공통 속성

| 속성/메서드 | 설명 |
|-----------|------|
| `product_id`, `name`, `base_price`, `is_available`, `product_type` | 기본 속성 |
| `calculate_price(selected_options: dict) → int` | base_price + Σ option.extra_price |
| `get_display_name() → str` | 화면 표시용 이름 |

**`Coffee(Product)`**, **`Gummy(Product)`** — product_type 고정값만 다름

---

### ingredient.py

**`Ingredient`** — 원재료 1종

| 속성/메서드 | 설명 |
|-----------|------|
| `ingredient_id`, `name`, `stock`, `max_capacity` | 기본 속성 |
| `is_available(needed: int) → bool` | stock >= needed |
| `deduct(amount: int) → None` | stock -= amount. 부족 시 `InsufficientStockException` |
| `replenish(amount: int) → None` | stock += amount. 초과 시 `StockOverflowException` |
| `remaining_capacity() → int` | max_capacity - stock |
| `is_out_of_stock() → bool` | stock == 0 |

---

### cart.py

**`OrderItem`** — 장바구니 항목 1개 (재고 확인 포함 — Recipe 통합)

| 속성/메서드 | 설명 |
|-----------|------|
| `product`, `selected_options: dict`, `quantity: int` | 기본 속성 |
| `calculate_subtotal() → int` | product.calculate_price(options) × quantity |
| `get_summary() → str` | "아메리카노 / Large / ICE × 2" 형태 |
| `get_required() → dict[str, int]` | 선택된 옵션 기반 총 원재료 소비량 계산 |
| `can_fulfill(ingredients: dict) → bool` | 모든 원재료 충분한지 확인 |

**`Cart`** — 장바구니 (할인 로직 미포함 — Controller에서 처리)

| 속성/메서드 | 설명 |
|-----------|------|
| `items: list[OrderItem]` | 담긴 항목 목록 |
| `add_item(item) → None` | 항목 추가 |
| `remove_item(index) → None` | 인덱스 항목 삭제 |
| `update_quantity(index, qty) → None` | 수량 변경 |
| `get_subtotal() → int` | Σ item.calculate_subtotal() |
| `is_empty() → bool` | 항목 없음 여부 |
| `clear() → None` | 전체 비우기 |

---

### payment.py

**`ChangeReserve`** — 키오스크 내 잔돈 보유량

| 속성/메서드 | 설명 |
|-----------|------|
| `reserve: dict[int, int]` | {10000: n, 5000: n, 1000: n, 500: n, 100: n} |
| `can_make_change(amount) → bool` | 그리디 시뮬레이션 — 반환 가능 여부 |
| `dispense(amount) → dict[int, int]` | 그리디 계산 후 reserve 차감, 반환 내역 리턴. 불가 시 `InsufficientChangeException` |
| `add_cash(denomination, count) → None` | 관리자 현금 보충 |
| `get_total() → int` | 보유 현금 총액 |

**`Payment`** (base)

| 속성/메서드 | 설명 |
|-----------|------|
| `amount: int` | 결제 금액 |
| `process() → bool` | 결제 실행 (하위 클래스에서 구현) |

**`CashPayment(Payment)`**

| 속성/메서드 | 설명 |
|-----------|------|
| `inserted_amount: int` | 현재까지 투입된 누적 금액 |
| `change_reserve: ChangeReserve` | 잔돈 처리 위임 |
| `insert(denomination: int) → None` | inserted_amount += denomination |
| `can_complete() → bool` | inserted_amount >= amount |
| `get_change_amount() → int` | inserted_amount - amount |
| `process() → dict[int, int]` | 잔돈 계산 후 반환 내역. `InsufficientChangeException` 가능 |

**`CardPayment(Payment)`**

| 속성/메서드 | 설명 |
|-----------|------|
| `process() → bool` | 시뮬레이션. try/except 내부 처리, 성공 반환 |

---

### discount.py

**`BundleDiscount`** — 할인 규칙 1개

| 속성/메서드 | 설명 |
|-----------|------|
| `name`, `condition_type`, `condition_value` | 조건 (예: "item_count >= 2") |
| `discount_rate`, `discount_amount` | 할인율 또는 고정 할인 금액 (둘 중 하나 사용) |
| `is_applicable(subtotal, item_count) → bool` | 조건 충족 여부 |
| `calculate(subtotal) → int` | 할인 금액 계산 |

**`DiscountPolicy`** — 할인 규칙 집합

| 속성/메서드 | 설명 |
|-----------|------|
| `rules: list[BundleDiscount]` | 등록된 할인 규칙 목록 |
| `apply(subtotal, item_count) → int` | 적용 가능한 규칙 중 최대 할인액 반환 |
| `add_rule(rule) → None` | 규칙 추가 |
| `remove_rule(name) → None` | 규칙 삭제 |

---

### stats.py

**`Statistics`** — 판매 통계 및 원재료 사용 통계

| 속성/메서드 | 설명 |
|-----------|------|
| `sales: dict` | {product_type: count} |
| `ingredients_used: dict` | {ingredient_id: count} |
| `revenue: int` | 누적 매출 |
| `record(order_items, amount) → None` | 결제 완료 시 통계 갱신 |
| `get_popular(n) → list[tuple]` | 판매 상위 n개 상품 |
| `get_hot_ingredients(threshold) → list[str]` | 사용 비율 >= threshold 원재료 |
| `to_dict() / from_dict(data)` | JSON 직렬화/역직렬화 |

---

### data_manager.py

**`DataManager`** — JSON 파일 읽기/쓰기 전담

| 메서드 | 설명 |
|--------|------|
| `load_products() → list[dict]` | products.json 읽기 |
| `save_products(data) → None` | products.json 쓰기 |
| `load_ingredients() → list[dict]` | ingredients.json 읽기 |
| `save_ingredients(data) → None` | ingredients.json 쓰기 |
| `load_recipes() → dict` | recipes.json 읽기. 형식 오류 시 `InvalidRecipeException` |
| `save_recipes(data) → None` | recipes.json 쓰기 |
| `load_options() → list[dict]` | options.json 읽기 |
| `save_options(data) → None` | options.json 쓰기 |
| `load_change_reserve() → dict` | change_reserve.json 읽기 |
| `save_change_reserve(data) → None` | change_reserve.json 쓰기 |
| `load_stats() → dict` | stats.json 읽기 |
| `save_stats(data) → None` | stats.json 쓰기 |
| `load_discount_policy() → list[dict]` | discount_policy.json 읽기 |
| `save_discount_policy(data) → None` | discount_policy.json 쓰기 |
| `load_admin_config() → dict` | admin_config.json 읽기 |
| `save_admin_config(data) → None` | admin_config.json 쓰기 |

---

### kiosk_controller.py

**`KioskController`** — 모든 비즈니스 로직의 조율자

생성자 파라미터:
```
products, ingredients, recipes, cart,
change_reserve, stats, discount_policy,
admin_config, data_manager,
logger=None   ← GUI 연동 시 사용
```

| 메서드 그룹 | 메서드 | 설명 |
|-----------|--------|------|
| **상품** | `get_available_products() → list` | 판매 가능 상품 목록 (is_available=True) |
| | `get_option_groups(product) → list` | 상품에 적용되는 옵션 그룹 |
| | `get_unavailable_options(product, selected) → set` | 재고 부족으로 선택 불가 옵션 ID |
| **장바구니** | `add_to_cart(product, options, qty) → None` | 레시피 가용성 확인 후 추가 |
| | `remove_from_cart(index) → None` | 항목 삭제 |
| | `update_cart_qty(index, qty) → None` | 수량 변경 |
| | `get_cart_subtotal() → int` | cart.get_subtotal() |
| | `get_discount() → int` | discount_policy.apply(subtotal, item_count) |
| | `get_final_amount() → int` | subtotal - discount |
| **결제** | `process_cash_payment() → dict` | CashPayment.process() → 재고차감 → 통계 → 저장 |
| | `process_card_payment() → bool` | CardPayment.process() → 재고차감 → 통계 → 저장 |
| | `insert_cash(denomination) → int` | CashPayment.insert() → inserted_amount 반환 |
| | `cancel_payment() → int` | 투입 금액 반환 |
| **관리자** | `authenticate_admin(pw) → bool` | 비밀번호 검증. 실패 시 `AdminAuthException` |
| | `admin_replenish(ingredient_id, amount)` | Ingredient.replenish() → ingredients.json 저장 |
| | `admin_set_price(product_id, price)` | 가격 변경 → products.json 저장 |
| | `admin_toggle_product(product_id, flag)` | ON/OFF → products.json 저장 |
| | `admin_set_discount(rules)` | discount_policy 갱신 → discount_policy.json 저장 |
| | `admin_get_stats() → dict` | stats 조회 |
| | `admin_set_config(top_n, threshold)` | admin_config.json 저장 |
| | `admin_change_password(new_pw)` | admin_config.json 저장 |
| | `admin_update_recipe(data)` | recipes.json 저장 |
| **내부** | `_deduct_stock(cart) → None` | 레시피 기반 원재료 차감 |
| | `_update_stats(cart, amount) → None` | stats.record() → stats.json 저장 |
| | `log(msg) → None` | logger 콜백 호출 (없으면 무시) |

---

### cli_view.py

**`CLIView`** — 터미널 인터페이스. controller만 알고 있음

| 메서드 | 설명 |
|--------|------|
| `run() → None` | 메인 루프. 상태 전이 관리 |
| `show_main_menu() → str` | 메뉴 출력 → 입력 받기 |
| `show_coffee_customization() → tuple` | 단계별 커피 옵션 선택 → (selected_options, quantity) |
| `show_gummy_customization() → tuple` | 단계별 구미 옵션 선택 → (selected_options, quantity) |
| `show_cart() → str` | 장바구니 + 할인 + 합계 출력 → 사용자 선택 |
| `show_payment_menu() → str` | 결제 수단 선택 |
| `show_cash_payment() → None` | 권종 선택 루프 → 결제 완료 |
| `show_admin_menu() → None` | 관리자 기능 메뉴 |
| `_get_int_input(prompt, min, max) → int` | 정수 입력 유효성 검증 내장 |
| `_get_choice(options: list) → int` | 번호 선택 유효성 검증 내장 |
| `_print_separator() → None` | 구분선 출력 |

---

### main.py

역할: 모든 객체를 생성하고 연결한다

```
흐름:
1. DataManager 생성
2. JSON 파일 로드 (8개)
3. 로드된 dict → 모델 객체 변환
   (Ingredient, Recipe, Product, OptionGroup, ChangeReserve, Statistics, DiscountPolicy)
4. KioskController 생성 (모든 모델 주입)
5. CLIView 생성 (controller 주입)
6. view.run() 호출
```

---

## 4. 패키징 설정 (pyproject.toml)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "kiosk"
version = "0.1.0"
requires-python = ">=3.12"

[tool.hatch.build.targets.wheel]
packages = ["src/app"]

[tool.pyright]
extraPaths = ["src"]
```

**역할:**
- `[tool.hatch.build.targets.wheel]` — `src/app/` 을 패키지 루트로 지정. `pip install -e .` 시 `app.*` import 가능
- `[tool.pyright]` — Pylance가 `src/` 를 검색 경로에 추가 → `Import could not be resolved` 경고 해소

**빌드 방법 (README.md 참고):**
```
pip install -e .                    # 개발 중 editable install
python -m unittest discover -s tests  # PYTHONPATH 불필요
```

---

## 5. 설계 결정 이유

| 결정 | 이유 |
|------|------|
| **Cart에 할인 로직 미포함** | Cart는 항목 보관만 담당. 할인 계산은 Controller에서 수행 → 순환 의존 방지 |
| **CLIView가 Controller만 참조** | GUI 전환 시 CLIView만 교체하면 됨. 모델 클래스 변경 불필요 |
| **DataManager 별도 분리** | JSON 경로 변경 / 파일 형식 변경 시 DataManager만 수정 |
| **logger=None 파라미터** | GUI 연동 시 Controller 코드 변경 없이 터미널 로그 출력 가능 |
| **KioskException base class** | 모든 키오스크 예외를 한 번에 catch 가능, 개별 catch도 가능 |
| **Recipe가 옵션 조합을 처리** | 원재료 소비 계산 책임을 Recipe에 집중 → Controller 단순화 |
| **ChangeReserve 별도 클래스** | 잔돈 그리디 계산과 보유량 관리를 캡슐화 → 단위 테스트 용이 |

---

## 5. 테스트 가능성 확보 포인트

| 클래스 | 테스트 가능 이유 |
|--------|--------------|
| `Ingredient` | 외부 의존 없음 — 단위 테스트 직접 가능 |
| `Recipe` | dict 입력/출력 — mock 없이 테스트 |
| `Cart` | 순수 계산 — 완전 독립 테스트 |
| `ChangeReserve` | 그리디 알고리즘 검증 — 독립 테스트 |
| `DiscountPolicy` | 조건/금액 입력 → 결과 검증 |
| `Statistics` | dict in/out — 독립 테스트 |
| `KioskController` | 모델 객체 주입 방식 → mock 객체로 교체 가능 |
| `DataManager` | 임시 JSON 파일로 테스트 가능 |