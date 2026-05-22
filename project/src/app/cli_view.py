import datetime
import msvcrt

from app.exceptions import (
    AdminAuthException, InsufficientChangeException, PaymentException,
    InsufficientStockException,
)
from app.payment import ChangeReserve


class CLIView:
    SEP = "─" * 40

    def __init__(self, controller):
        self.controller = controller

    # ── 메인 루프 ───────────────────────────────────────────────
    def run(self) -> None:
        while True:
            self._show_idle()
            self._run_session()

    def _show_idle(self) -> None:
        import sys
        self._print_separator()
        print("   Micro-Factory Kiosk")
        print()
        print("   원하시는 음료와 영양 구미를")
        print("   자유롭게 커스텀하여 주문하세요.")
        print()
        print("   화면을 터치하면 시작합니다.")
        self._print_separator()
        sys.stdout.flush()
        if sys.stdin.isatty():
            msvcrt.getch()
        else:
            sys.stdin.buffer.read(1)

    def _run_session(self) -> None:
        # 새 세션마다 장바구니 초기화
        if not self.controller.cart.is_empty():
            self.controller.cart.clear(self.controller.ingredients)
        while True:
            choice = self.show_main_menu()
            if choice == "1":
                self._handle_product("coffee")
            elif choice == "2":
                self._handle_product("gummy")
            elif choice == "3":
                self._handle_cart_view()
            elif choice == "4":
                self._handle_admin_auth()
            elif choice == "0":
                print("처음 화면으로 돌아갑니다.")
                break

    def show_main_menu(self) -> str:
        self._print_separator()

        # 장바구니 항시 표시
        if not self.controller.cart.is_empty():
            print("[ 장바구니 현황 ]")
            for item in self.controller.cart.items:
                print(f"  • {item.get_summary()}  {item.calculate_subtotal():,}원")
            print(f"  합계: {self.controller.get_final_amount():,}원")
            self._print_separator()

        products = self.controller.get_available_products()
        coffee_ok = any(p.product_type == "coffee" for p in products)
        gummy_ok  = any(p.product_type == "gummy"  for p in products)
        print("[ 주문 메뉴 ]")
        print(f"  1. 커피 주문{'' if coffee_ok else ' (품절)'}")
        print(f"  2. 구미 주문{'' if gummy_ok  else ' (품절)'}")
        print("  3. 수량 변경")
        print("  4. 관리자")
        print("  0. 처음 화면")
        return input("선택: ").strip()

    # ── 상품 선택 / 커스텀 ────────────────────────────────────
    def _handle_product(self, product_type: str) -> None:
        products = [p for p in self.controller.get_available_products()
                    if p.product_type == product_type]
        if not products:
            print("현재 주문 가능한 상품이 없습니다.")
            return

        label = "커피" if product_type == "coffee" else "구미"
        self._print_separator()
        print(f"[ {label} 선택 ]")
        for i, p in enumerate(products, 1):
            print(f"  {i}. {p.get_display_name()}  ({p.base_price:,}원~)")
        print("  0. 뒤로")
        idx = self._get_cancelable_int("선택: ", 1, len(products))
        if idx is None:
            return
        product = products[idx - 1]

        selected, qty = self._customize(product)
        if selected is None:
            return

        price = product.calculate_price(selected) * qty
        print(f"\n예상 금액: {price:,}원")
        while True:
            confirm = input("장바구니에 추가할까요? (y/n): ").strip().lower()
            if confirm in ("y", "n"):
                break
            print("  y 또는 n을 입력하세요.")
        if confirm != "y":
            return
        try:
            self.controller.add_to_cart(product, selected, qty)
            print("장바구니에 추가되었습니다.")
        except InsufficientStockException as e:
            print(f"재고 부족: {e}")

    def _customize(self, product) -> tuple:
        selected = {}
        for group in self.controller.get_option_groups(product):
            options = group.get_options()
            self._print_separator()
            print(f"[ {group.name} ]")
            unavailable = self.controller.get_unavailable_options(product, selected)
            for i, opt in enumerate(options, 1):
                price_str = f" (+{opt.extra_price:,}원)" if opt.extra_price else ""
                stock_str = "  ※재고부족" if opt.option_id in unavailable else ""
                print(f"  {i}. {opt.name}{price_str}{stock_str}")
            print("  0. 뒤로")
            idx = self._get_cancelable_int("선택: ", 1, len(options))
            if idx is None:
                return None, None
            selected[group.group_id] = options[idx - 1]
        qty = self._get_cancelable_int("수량 입력 (0=뒤로): ", 1, 99)
        if qty is None:
            return None, None
        return selected, qty

    # ── 장바구니 ───────────────────────────────────────────────
    def _handle_cart_view(self) -> None:
        while True:
            result = self.show_cart()
            if result == "pay":
                self._handle_payment()
                return
            elif result in ("empty", "exit"):
                return

    def show_cart(self) -> str:
        self._print_separator()
        if self.controller.cart.is_empty():
            print("장바구니가 비어 있습니다.")
            return "empty"

        print("[ 장바구니 ]")
        for i, item in enumerate(self.controller.cart.items):
            print(f"  {i+1}. {item.get_summary()}  {item.calculate_subtotal():,}원")

        subtotal = self.controller.get_cart_subtotal()
        final    = self.controller.get_final_amount()
        print(f"\n  소계: {subtotal:,}원")
        if subtotal != final:
            print(f"  할인: -{subtotal - final:,}원")
        print(f"  합계: {final:,}원")

        print("\n  1. 결제 진행  2. 수량 변경  3. 장바구니 비우기  0. 계속 쇼핑")
        choice = input("선택: ").strip()
        if choice == "1":
            return "pay"
        elif choice == "2":
            items = self.controller.cart.items
            idx = self._get_cancelable_int("변경할 번호 (0=뒤로): ", 1, len(items))
            if idx is not None:
                item = items[idx - 1]
                print(f"  선택: {item.get_summary()}  (현재 {item.quantity}개)")
                print("  ※ 수량을 0으로 입력하면 항목이 삭제됩니다.")
                qty = self._get_int_input("새 수량 (0=삭제): ", 0, 99)
                if qty == 0:
                    self.controller.remove_from_cart(idx - 1)
                    print("항목이 삭제되었습니다.")
                else:
                    try:
                        self.controller.update_cart_qty(idx - 1, qty)
                        print(f"수량이 {qty}개로 변경되었습니다.")
                    except Exception as e:
                        print(f"오류: {e}")
            return "stay"
        elif choice == "3":
            while True:
                confirm = input("정말 비우시겠습니까? (y/n): ").strip().lower()
                if confirm in ("y", "n"):
                    break
                print("  y 또는 n을 입력하세요.")
            if confirm == "y":
                self.controller.cart.clear(self.controller.ingredients)
                print("장바구니를 비웠습니다.")
                return "empty"
            return "stay"
        return "exit"

    # ── 결제 ──────────────────────────────────────────────────
    def _handle_payment(self) -> None:
        choice = self.show_payment_menu()
        if choice == "1":
            self.show_cash_payment()
        elif choice == "2":
            self._process_card()

    def show_payment_menu(self) -> str:
        self._print_separator()
        print(f"[ 결제 수단 선택 ]  결제 금액: {self.controller.get_final_amount():,}원")
        print("  1. 현금  2. 카드  0. 취소")
        choice = input("선택: ").strip()
        if choice == "0":
            print("결제를 취소했습니다.")
        return choice

    def show_cash_payment(self) -> None:
        self.controller.start_cash_payment()
        denoms = sorted(ChangeReserve.DENOMINATIONS)  # 오름차순 표시
        print("\n[ 현금 투입 ]")
        while True:
            pmt   = self.controller._active_payment
            final = self.controller.get_final_amount()
            ins   = pmt.inserted_amount if pmt else 0
            print(f"  결제: {final:,}원 / 투입: {ins:,}원 / 잔액: {max(0, final - ins):,}원")
            for i, d in enumerate(denoms, 1):
                print(f"  {i}. {d:,}원")
            print(f"  {len(denoms)+1}. 결제  0. 취소")
            choice = input("선택: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(denoms):
                self.controller.insert_cash(denoms[int(choice) - 1])
            elif choice == str(len(denoms) + 1):
                if not self.controller.can_complete_payment():
                    print("투입 금액이 부족합니다.")
                    continue
                # 영수증용 스냅샷 (처리 전 캡처)
                snapshot = list(self.controller.cart.items)
                final_amt = self.controller.get_final_amount()
                try:
                    change_result = self.controller.process_cash_payment()
                    self._print_receipt(snapshot, final_amt, "현금", change_result)
                    break
                except InsufficientChangeException:
                    refund = self.controller.cancel_payment()
                    print(f"잔돈 부족. 투입 금액 {refund:,}원을 반환합니다.")
                    break
            elif choice == "0":
                refund = self.controller.cancel_payment()
                print(f"취소. {refund:,}원 반환.")
                break

    def _process_card(self) -> None:
        self.controller.start_card_payment()
        print("카드를 태그해 주세요...")
        # 영수증용 스냅샷 (처리 전 캡처)
        snapshot = list(self.controller.cart.items)
        final_amt = self.controller.get_final_amount()
        try:
            self.controller.process_card_payment()
            self._print_receipt(snapshot, final_amt, "카드")
        except PaymentException as e:
            print(f"카드 결제 실패: {e}")
            self.controller.cancel_payment()

    def _print_receipt(self, items: list, final_amount: int,
                       payment_method: str, change_result: dict | None = None) -> None:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._print_separator()
        print("           [ 영  수  증 ]")
        print(f"  일시: {now}")
        self._print_separator()
        for item in items:
            print(f"  {item.get_summary()}")
            print(f"      {item.calculate_subtotal():>10,}원")
        self._print_separator()
        subtotal = sum(i.calculate_subtotal() for i in items)
        if subtotal != final_amount:
            print(f"  소계:          {subtotal:>10,}원")
            print(f"  할인:         -{subtotal - final_amount:>10,}원")
        print(f"  합계:          {final_amount:>10,}원")
        print(f"  결제 수단:      {payment_method}")
        if change_result is not None:
            if change_result:
                print("  잔돈:")
                for denom, cnt in sorted(change_result.items(), reverse=True):
                    print(f"    {denom:,}원 × {cnt}장")
            else:
                print("  잔돈: 없음")
        self._print_separator()
        print("      감사합니다! 또 이용해 주세요.")
        self._print_separator()

    # ── 관리자 ─────────────────────────────────────────────────
    def _handle_admin_auth(self) -> None:
        self._print_separator()
        pw = input("관리자 비밀번호: ").strip()
        try:
            self.controller.authenticate_admin(pw)
            self.show_admin_menu()
        except AdminAuthException as e:
            print(f"인증 실패: {e}")

    def show_admin_menu(self) -> None:
        while True:
            self._print_separator()
            print("[ 관리자 메뉴 ]")
            print("  1. 재고 보충     2. 상품 ON/OFF")
            print("  3. 가격 변경     4. 현금 보유량 확인")
            print("  5. 비밀번호 변경  6. 키오스크 종료")
            print("  0. 관리자 메뉴 종료")
            choice = input("선택: ").strip()
            if choice == "1":
                self._admin_replenish()
            elif choice == "2":
                self._admin_toggle()
            elif choice == "3":
                self._admin_set_price()
            elif choice == "4":
                reserve = self.controller.change_reserve
                total   = reserve.get_total()
                print(f"현금 보유량: {total:,}원")
                for denom in sorted(reserve.reserve.keys(), reverse=True):
                    count = reserve.reserve[denom]
                    print(f"  {denom:,}원권: {count}장")
            elif choice == "5":
                new_pw = input("새 비밀번호 (빈 입력=뒤로): ").strip()
                if not new_pw:
                    print("취소했습니다.")
                else:
                    self.controller.admin_change_password(new_pw)
                    print("변경되었습니다.")
            elif choice == "6":
                while True:
                    confirm = input("키오스크를 종료하시겠습니까? (y/n): ").strip().lower()
                    if confirm in ("y", "n"):
                        break
                    print("  y 또는 n을 입력하세요.")
                if confirm == "y":
                    print("키오스크를 종료합니다.")
                    import sys
                    sys.exit(0)
            elif choice == "0":
                break

    def _admin_replenish(self) -> None:
        ings = list(self.controller.ingredients.values())
        print("  [ 원재료 목록 ]")
        print(f"  {'번호':<4} {'ID':<12} {'이름':<10} {'현재 재고':>10}  {'최대':>8}")
        print("  " + "─" * 50)
        for i, ing in enumerate(ings, 1):
            stock_str = f"{ing.stock}{ing.unit}"
            max_str   = f"{ing.max_capacity}{ing.unit}"
            print(f"  {i:<4} {ing.ingredient_id:<12} {ing.name:<10} {stock_str:>10}  {max_str:>8}")
        idx = self._get_cancelable_int("  번호 선택 (0=뒤로): ", 1, len(ings))
        if idx is None:
            return
        ing = ings[idx - 1]
        remaining = ing.remaining_capacity()
        print(f"  선택: {ing.name} (ID: {ing.ingredient_id}) | 보충 가능량: {remaining}{ing.unit}")
        amount = self._get_cancelable_int(f"보충량 (1~{remaining}, 0=뒤로): ", 1, remaining)
        if amount is None:
            return
        try:
            self.controller.admin_replenish(ing.ingredient_id, amount)
            stock = self.controller.ingredients[ing.ingredient_id].stock
            print(f"보충 완료. 현재 재고: {stock}{ing.unit}")
        except Exception as e:
            print(f"오류: {e}")

    def _admin_toggle(self) -> None:
        pid = self._get_product_id()
        if pid is None:
            return

        while True:
            raw = input("판매 상태 (on/off, 0=뒤로): ").strip().lower()
            if raw == "0":
                return
            if raw in ("on", "off"):
                break
            print("  on 또는 off만 입력하세요.")

        self.controller.admin_toggle_product(pid, raw == "on")
        state = "판매 중" if raw == "on" else "판매 중지"
        print(f"변경되었습니다. ({state})")

    def _admin_set_price(self) -> None:
        pid = self._get_product_id()
        if pid is None:
            return
        price = self._get_int_input("새 가격 (원, 0=뒤로): ", 0, 999999)
        if price == 0:
            confirm = input("0원으로 설정하시겠습니까? (y/n): ").strip().lower()
            if confirm != "y":
                return
        self.controller.admin_set_price(pid, price)
        print(f"변경되었습니다. ({price:,}원)")

    def _get_product_id(self) -> str | None:
        """상품 목록을 번호로 보여주고 선택받는다. 0이면 None 반환."""
        prods = self.controller.products
        print("  [ 상품 목록 ]")
        print(f"  {'번호':<4} {'ID':<6} {'이름':<12} {'가격':>8}  {'상태'}")
        print("  " + "─" * 40)
        for i, p in enumerate(prods, 1):
            state = "판매중" if p.is_available else "판매중지"
            print(f"  {i:<4} {p.product_id:<6} {p.name:<12} {p.base_price:>7,}원  {state}")
        idx = self._get_cancelable_int("  번호 선택 (0=뒤로): ", 1, len(prods))
        if idx is None:
            return None
        p = prods[idx - 1]
        print(f"  선택: {p.name} (ID: {p.product_id})")
        return p.product_id

    # ── 헬퍼 ──────────────────────────────────────────────────
    def _get_int_input(self, prompt: str, min_val: int, max_val: int) -> int:
        while True:
            try:
                val = int(input(prompt))
                if min_val <= val <= max_val:
                    return val
                print(f"  {min_val}~{max_val} 사이 숫자를 입력하세요.")
            except ValueError:
                print("  숫자를 입력하세요.")

    def _get_cancelable_int(self, prompt: str, min_val: int, max_val: int) -> int | None:
        """0 입력 시 None(뒤로가기), 그 외 min~max 범위 정수 반환."""
        while True:
            try:
                val = int(input(prompt))
                if val == 0:
                    return None
                if min_val <= val <= max_val:
                    return val
                print(f"  0(뒤로) 또는 {min_val}~{max_val} 사이 숫자를 입력하세요.")
            except ValueError:
                print("  숫자를 입력하세요.")

    def _get_choice(self, options: list) -> int:
        return self._get_int_input("선택: ", 1, len(options))

    def _print_separator(self) -> None:
        print(self.SEP)
