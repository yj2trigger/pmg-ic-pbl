import datetime
import sys

from app.cart import Cart, OrderItem
from app.drug_controller import DrugController
from app.exceptions import InsufficientChangeException, PaymentException
from app.payment import CashPayment, CardPayment, ChangeReserve


class CLIView:
    SEP = "─" * 40

    def __init__(self, controller: DrugController, cart: Cart, change_reserve: ChangeReserve):
        self.controller = controller
        self.cart = cart
        self.change_reserve = change_reserve

    # ── 메인 루프 ──────────────────────────────────────
    def run(self) -> None:
        while True:
            self._show_idle()
            self._run_session()

    def _show_idle(self) -> None:
        self._print_separator()
        print("   EDK — Erica Drug King")
        print()
        print("   증상에 맞는 의약품을")
        print("   찾아 구매하세요.")
        print()
        print("   화면을 터치하면 시작합니다.")
        self._print_separator()
        sys.stdout.flush()
        try:
            import msvcrt
            msvcrt.getch()
        except ImportError:
            sys.stdin.buffer.read(1)

    def _run_session(self) -> None:
        if not self.cart.is_empty():
            self.cart.clear({})
        while True:
            choice = self._show_main_menu()
            if choice == "1":
                self._handle_symptom_select()
            elif choice == "2":
                self._handle_all_medicines()
            elif choice == "3":
                self._handle_cart_view()
            elif choice == "4":
                self._handle_admin_auth()
            elif choice == "0":
                print("첫 화면으로 돌아갑니다.")
                break

    def _show_main_menu(self) -> str:
        self._print_separator()
        if not self.cart.is_empty():
            print("[ 장바구니 현황 ]")
            for item in self.cart.items:
                print(f"  • {item.get_summary()}  {item.calculate_subtotal():,}원")
            print(f"  합계: {self.cart.get_subtotal():,}원")
            self._print_separator()
        print("[ 메뉴 ]")
        print("  1. 증상으로 찾기")
        print("  2. 전체 의약품 보기")
        print("  3. 장바구니")
        print("  4. 관리자")
        print("  0. 첫 화면")
        return input("선택: ").strip()

    # ── 증상 선택 ──────────────────────────────────
    def _handle_symptom_select(self) -> None:
        group = self.controller.get_all_symptoms()
        symptoms = group.symptoms
        if not symptoms:
            print("등록된 증상이 없습니다.")
            return
        self._print_separator()
        print("[ 증상 선택 ]")
        for i, s in enumerate(symptoms, 1):
            mark = "  ⚠ 응급" if s.is_emergency else ""
            print(f"  {i}. {s.name}{mark}")
        print("  0. 뒤로")
        idx = self._get_cancelable_int("선택: ", 1, len(symptoms))
        if idx is None:
            return
        symptom = symptoms[idx - 1]
        if symptom.is_emergency:
            self._print_separator()
            print(f"  ⚠  '{symptom.name}'은(는) 응급 증상입니다.")
            print()
            print("  즉시 119에 연락하거나")
            print("  가까운 응급실을 방문하세요.")
            self._print_separator()
            input("  확인 후 Enter...")
            return
        medicines = self.controller.get_medicines_for_symptom(symptom.name)
        self._show_medicine_list(medicines, f"[ '{symptom.name}' 관련 의약품 ]")

    def _handle_all_medicines(self) -> None:
        medicines = self.controller.get_available_medicines()
        self._show_medicine_list(medicines, "[ 전체 의약품 ]")

    def _show_medicine_list(self, medicines: list, title: str) -> None:
        if not medicines:
            print("표시할 의약품이 없습니다.")
            return
        while True:
            self._print_separator()
            print(title)
            for i, m in enumerate(medicines, 1):
                cats = ", ".join(m.symptom_categories) if m.symptom_categories else "-"
                print(f"  {i}. {m.name}  {m.base_price:,}원  [{cats}]")
            print("  0. 뒤로")
            idx = self._get_cancelable_int("선택 (상세 보기): ", 1, len(medicines))
            if idx is None:
                return
            self._show_medicine_detail(medicines[idx - 1])

    def _show_medicine_detail(self, medicine) -> None:
        self._print_separator()
        print(f"[ {medicine.name} ]")
        print(f"  가격: {medicine.base_price:,}원")
        if medicine.description:
            print(f"  설명: {medicine.description}")
        if medicine.dosage:
            print(f"  용법: {medicine.dosage}")
        if medicine.caution:
            print(f"  주의: {medicine.caution}")
        cats = ", ".join(medicine.symptom_categories) if medicine.symptom_categories else "-"
        print(f"  증상: {cats}")
        print()
        print("  1. 장바구니 담기  0. 뒤로")
        choice = input("선택: ").strip()
        if choice != "1":
            return
        qty = self._get_cancelable_int("수량 (0=뒤로): ", 1, 99)
        if qty is None:
            return
        item = OrderItem(medicine, {}, qty)
        self.cart.add_item(item, {})
        print(f"'{medicine.name}' {qty}개를 장바구니에 추가했습니다.")

    # ── 장바구니 ───────────────────────────────────
    def _handle_cart_view(self) -> None:
        while True:
            result = self._show_cart()
            if result == "pay":
                self._handle_payment()
                return
            elif result in ("empty", "exit"):
                return

    def _show_cart(self) -> str:
        self._print_separator()
        if self.cart.is_empty():
            print("장바구니가 비어 있습니다.")
            return "empty"
        print("[ 장바구니 ]")
        for i, item in enumerate(self.cart.items, 1):
            print(f"  {i}. {item.get_summary()}  {item.calculate_subtotal():,}원")
        print(f"\n  합계: {self.cart.get_subtotal():,}원")
        print("\n  1. 결제 진행  2. 항목 삭제  3. 장바구니 비우기  0. 계속 쿠핑")
        choice = input("선택: ").strip()
        if choice == "1":
            return "pay"
        elif choice == "2":
            idx = self._get_cancelable_int("삭제할 번호 (0=뒤로): ", 1, len(self.cart.items))
            if idx is not None:
                self.cart.remove_item(idx - 1, {})
                print("삭제되었습니다.")
        elif choice == "3":
            confirm = input("정말 비우시겠습니까? (y/n): ").strip().lower()
            if confirm == "y":
                self.cart.clear({})
                print("장바구니를 비웠습니다.")
                return "empty"
        return "stay"

    # ── 결제 ──────────────────────────────────────
    def _handle_payment(self) -> None:
        total = self.cart.get_subtotal()
        self._print_separator()
        print(f"[ 결제 수단 선택 ]  결제 금액: {total:,}원")
        print("  1. 현금  2. 카드  0. 취소")
        choice = input("선택: ").strip()
        if choice == "1":
            self._process_cash(total)
        elif choice == "2":
            self._process_card(total)
        else:
            print("결제를 취소했습니다.")

    def _process_cash(self, total: int) -> None:
        payment = CashPayment(total, self.change_reserve)
        denoms = sorted(ChangeReserve.DENOMINATIONS)
        print("\n[ 현금 투입 ]")
        while True:
            ins = payment.inserted_amount
            print(f"  결제: {total:,}원 / 투입: {ins:,}원 / 잔액: {max(0, total - ins):,}원")
            for i, d in enumerate(denoms, 1):
                print(f"  {i}. {d:,}원")
            print(f"  {len(denoms)+1}. 결제  0. 취소")
            choice = input("선택: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(denoms):
                payment.insert(denoms[int(choice) - 1])
            elif choice == str(len(denoms) + 1):
                if not payment.can_complete():
                    print("투입 금액이 부족합니다.")
                    continue
                snapshot = list(self.cart.items)
                try:
                    change_result = payment.process()
                    self.controller._dm.save_change_reserve(
                        {str(k): v for k, v in self.change_reserve.reserve.items()}
                    )
                    self.cart.items = []
                    self._print_receipt(snapshot, total, "현금", change_result)
                    break
                except InsufficientChangeException:
                    print(f"잔돈 부족. 투입 금액 {payment.inserted_amount:,}원을 반환합니다.")
                    break
            elif choice == "0":
                print(f"취소. {payment.inserted_amount:,}원 반환.")
                break

    def _process_card(self, total: int) -> None:
        print("카드를 태그해 주세요...")
        payment = CardPayment(total)
        snapshot = list(self.cart.items)
        try:
            payment.process()
            self.cart.items = []
            self._print_receipt(snapshot, total, "카드")
        except PaymentException as e:
            print(f"카드 결제 실패: {e}")

    def _print_receipt(self, items: list, total: int, method: str,
                       change_result: dict | None = None) -> None:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._print_separator()
        print("           [ 영  수  증 ]")
        print(f"  일시: {now}")
        self._print_separator()
        for item in items:
            print(f"  {item.get_summary()}")
            print(f"      {item.calculate_subtotal():>10,}원")
        self._print_separator()
        print(f"  합계:          {total:>10,}원")
        print(f"  결제 수단:      {method}")
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

    # ── 관리자 ─────────────────────────────────────
    def _handle_admin_auth(self) -> None:
        self._print_separator()
        pw = input("관리자 비밀번호: ").strip()
        admin_config = self.controller._dm.load_admin_config()
        if pw != admin_config.get("password", ""):
            print("인증 실패: 비밀번호가 올바르지 않습니다.")
            return
        self._show_admin_menu(admin_config)

    def _show_admin_menu(self, admin_config: dict) -> None:
        while True:
            self._print_separator()
            print("[ 관리자 메뉴 ]")
            print("  1. 의약품 ON/OFF   2. 가격 변경")
            print("  3. 현금 보유량   4. 비밀번호 변경")
            print("  5. 키오스크 종료   0. 종료")
            choice = input("선택: ").strip()
            if choice == "1":
                self._admin_toggle_medicine()
            elif choice == "2":
                self._admin_set_price()
            elif choice == "3":
                total = self.change_reserve.get_total()
                print(f"현금 보유량: {total:,}원")
                for denom in sorted(self.change_reserve.reserve.keys(), reverse=True):
                    print(f"  {denom:,}원권: {self.change_reserve.reserve[denom]}장")
            elif choice == "4":
                new_pw = input("새 비밀번호 (빈 입력=뒤로): ").strip()
                if new_pw:
                    admin_config["password"] = new_pw
                    self.controller._dm.save_admin_config(admin_config)
                    print("변경되었습니다.")
            elif choice == "5":
                confirm = input("키오스크를 종료하시겠습니까? (y/n): ").strip().lower()
                if confirm == "y":
                    print("키오스크를 종료합니다.")
                    sys.exit(0)
            elif choice == "0":
                break

    def _admin_toggle_medicine(self) -> None:
        medicines = self.controller._dm.load_medicines()
        if not medicines:
            print("등록된 의약품이 없습니다.")
            return
        print("[ 의약품 목록 ]")
        for i, m in enumerate(medicines, 1):
            state = "판매중" if m.is_available else "판매중지"
            print(f"  {i}. {m.name}  ({state})")
        idx = self._get_cancelable_int("번호 선택 (0=뒤로): ", 1, len(medicines))
        if idx is None:
            return
        while True:
            raw = input("판매 상태 (on/off, 0=뒤로): ").strip().lower()
            if raw == "0":
                return
            if raw in ("on", "off"):
                break
        medicines[idx - 1].is_available = (raw == "on")
        self.controller._dm.save_medicines(medicines)
        print(f"변경되었습니다. ({'판매 중' if raw == 'on' else '판매 중지'})")

    def _admin_set_price(self) -> None:
        medicines = self.controller._dm.load_medicines()
        if not medicines:
            print("등록된 의약품이 없습니다.")
            return
        print("[ 의약품 목록 ]")
        for i, m in enumerate(medicines, 1):
            print(f"  {i}. {m.name}  {m.base_price:,}원")
        idx = self._get_cancelable_int("번호 선택 (0=뒤로): ", 1, len(medicines))
        if idx is None:
            return
        price = self._get_int_input("새 가격 (원): ", 0, 999999)
        medicines[idx - 1].base_price = price
        self.controller._dm.save_medicines(medicines)
        print(f"변경되었습니다. ({price:,}원)")

    # ── 헬퍼 ──────────────────────────────────────
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

    def _print_separator(self) -> None:
        print(self.SEP)
