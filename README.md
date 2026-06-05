# 아이스크림 키오스크 — UML 다이어그램

## 클래스 다이어그램

```mermaid
classDiagram
    class IceCreamProduct {
        +String product_id
        +String name
        +int base_price
        +bool is_available
        +String product_type
        +calculate_price(options) int
        +get_display_name() String
    }

    class Ingredient {
        +String ingredient_id
        +String name
        +int stock
        +int max_capacity
        +String unit
        +is_available(needed) bool
        +deduct(amount)
        +replenish(amount)
        +remaining_capacity() int
        +is_out_of_stock() bool
    }

    class Option {
        +String option_id
        +String name
        +int extra_price
        +dict required_ingredients_dic
    }

    class OptionGroup {
        +String group_id
        +String name
        -list _active_for
        -list _options
        +is_active_for(product_type) bool
        +get_options() list
    }

    class OrderItem {
        +IceCreamProduct product
        +dict selected_options
        +int quantity
        +calculate_subtotal() int
        +get_summary() String
        +get_required_ingredients() dict
        +can_fulfill(ingredients) bool
    }

    class Cart {
        +list items
        +add_item(item, ingredients)
        +remove_item(index, ingredients)
        +update_quantity(index, qty, ingredients)
        +get_subtotal() int
        +clear(ingredients)
    }

    class KioskController {
        +list products
        +dict ingredients
        +list option_groups
        +Cart cart
        +ChangeReserve change_reserve
        +dict admin_config
        +DataManager data_manager
        +get_available_products() list
        +add_to_cart(product, options, qty)
        +start_cash_payment()
        +process_cash_payment() dict
        +start_card_payment()
        +process_card_payment() bool
        +authenticate_admin(pw) bool
        +admin_replenish(ingredient_id, amount)
        +admin_set_price(product_id, price)
    }

    class Payment {
        <<abstract>>
        +int amount
        +process()*
    }

    class CashPayment {
        +int inserted_amount
        +dict inserted_bills
        +ChangeReserve change_reserve
        +insert(denomination)
        +can_complete() bool
        +get_change_amount() int
        +process() dict
    }

    class CardPayment {
        +str fail_reason
        +process() bool
    }

    class ChangeReserve {
        +dict reserve
        +DENOMINATIONS$ list
        +can_make_change(amount) bool
        +dispense(amount) dict
        +add_cash(denomination, count)
        +get_total() int
    }

    class DataManager {
        +String data_dir
        +load_products() list
        +save_products(products)
        +load_ingredients() dict
        +save_ingredients(list)
        +load_option_groups() list
        +load_change_reserve() dict
        +save_change_reserve(data)
        +load_admin_config() dict
        +save_admin_config(data)
    }

    class KioskException {
        <<exception>>
    }
    class StockOverflowException
    class InsufficientStockException
    class InsufficientChangeException
    class PaymentException
    class AdminAuthException

    KioskException <|-- StockOverflowException
    KioskException <|-- InsufficientStockException
    KioskException <|-- InsufficientChangeException
    KioskException <|-- PaymentException
    KioskException <|-- AdminAuthException

    Payment <|-- CashPayment
    Payment <|-- CardPayment

    OptionGroup "1" *-- "1..*" Option : contains

    Cart "1" *-- "0..*" OrderItem : contains
    OrderItem --> IceCreamProduct : references

    KioskController --> IceCreamProduct : uses
    KioskController --> Ingredient : manages
    KioskController --> OptionGroup : uses
    KioskController "1" *-- "1" Cart : has
    KioskController "1" *-- "1" ChangeReserve : has
    KioskController --> DataManager : uses

    CashPayment --> ChangeReserve : uses
```

---

```mermaid
sequenceDiagram
    actor User
    participant GUI
    participant Controller as KioskController
    participant Cart
    participant CP as CashPayment
    participant CR as ChangeReserve
    participant DM as DataManager
 
    note over User,DM: ① 상품 선택 & 장바구니 추가
    User->>GUI: 상품/옵션 선택 후 [담기] 클릭
    GUI->>Controller: add_to_cart(product, options, qty)
    Controller->>Cart: add_item(item, ingredients)
    Cart-->>Controller: 재고 차감 완료
    Controller-->>GUI: 장바구니 업데이트
 
    note over User,DM: ② 결제 방법 선택 — 현금
    User->>GUI: [현금 결제] 버튼 클릭
    GUI->>Controller: start_cash_payment()
    Controller->>CP: CashPayment(amount, change_reserve) 생성
    Controller-->>GUI: CashPaymentScreen 표시
 
    note over User,DM: ③ 지폐 투입
    User->>GUI: 지폐 투입 (예: 10,000원)
    GUI->>Controller: insert_cash(denomination=10000)
    Controller->>CP: insert(10000)
    CP-->>Controller: inserted_amount 반환
    Controller-->>GUI: 투입 금액 표시 갱신
 
    note over User,DM: ④ 결제 완료 처리
    User->>GUI: [결제 완료] 버튼 클릭
    GUI->>Controller: process_cash_payment()
    Controller->>CP: process()
    note over CP,CR: 버그 수정 (98770e0):<br/>투입 지폐를 reserve에 먼저 추가해야<br/>잔돈 계산이 정확함
    CP->>CR: add_cash(denom, count)
    CP->>CR: dispense(change_amount)
    CR-->>CP: {권종: 장수} 반환
    CP-->>Controller: change_breakdown 반환
    Controller->>DM: save_ingredients()
    Controller->>DM: save_change_reserve()
    DM-->>Controller: 저장 완료
 
    note over User,DM: ⑤ 영수증 출력
    Controller->>GUI: ReceiptScreen(change_breakdown)
    GUI-->>User: 영수증 + 잔돈 내역 표시
 
    note over User,DM: ⑥ 초기화
    Controller->>Cart: items = []
    GUI-->>User: IdleScreen으로 복귀
```
