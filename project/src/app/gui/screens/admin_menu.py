import sys

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QDialog, QComboBox, QSpinBox, QLineEdit, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AdminMenuScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(14)

        title = QLabel("관리자 메뉴")
        title.setFont(QFont("Malgun Gothic", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        grid = QGridLayout()
        grid.setSpacing(12)
        operations = [
            ("상품 ON/OFF",    self._toggle_product),
            ("재료 재고 보충",  self._replenish_ingredient),
            ("재고 현황 확인",  self._show_stock),
            ("현금 보유량 확인", self._show_cash),
            ("현금 추가",       self._add_cash),
            ("비밀번호 변경",   self._change_password),
            ("키오스크 종료",   self._shutdown),
        ]
        for i, (label, handler) in enumerate(operations):
            btn = QPushButton(label)
            btn.setMinimumHeight(68)
            btn.setFont(QFont("Malgun Gothic", 16))
            btn.clicked.connect(handler)
            grid.addWidget(btn, i // 2, i % 2)

        self._status_label = QLabel()
        self._status_label.setFont(QFont("Malgun Gothic", 13))
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("color: #a6e3a1;")

        btn_back = QPushButton("← 관리자 메뉴 종료")
        btn_back.setMinimumHeight(52)
        btn_back.clicked.connect(lambda: self._window.go_to_main_menu())

        layout.addWidget(title)
        layout.addLayout(grid)
        layout.addWidget(self._status_label)
        layout.addStretch()
        layout.addWidget(btn_back)

    def refresh(self) -> None:
        self._status_label.setText("")

    def _toggle_product(self) -> None:
        ctrl = self._window.controller
        dlg = _ToggleProductDialog(ctrl.products, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            pid, flag = dlg.result_data
            state = "판매 중" if flag else "판매 중지"
            product = next((p for p in ctrl.products if p.product_id == pid), None)
            name = product.name if product else pid
            confirm = QMessageBox.question(
                self, "변경 확인",
                f"[{name}]을(를) '{state}'으로 변경하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if confirm == QMessageBox.StandardButton.Yes:
                ctrl.admin_toggle_product(pid, flag)
                self._status_label.setText(f"변경 완료: {name} → {state}")

    def _replenish_ingredient(self) -> None:
        ctrl = self._window.controller
        dlg = _ReplenishDialog(list(ctrl.ingredients.values()), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            iid, amount = dlg.result_data
            try:
                ctrl.admin_replenish(iid, amount)
                self._status_label.setText(
                    f"보충 완료: {ctrl.ingredients[iid].name}  +{amount}개"
                )
            except Exception as e:
                QMessageBox.warning(self, "보충 실패", str(e))

    def _show_stock(self) -> None:
        ctrl = self._window.controller
        lines = ["[ 재료 재고 현황 ]\n"]
        for ing in ctrl.ingredients.values():
            ratio = (ing.stock / ing.max_capacity) if ing.max_capacity > 0 else 0
            bar = "█" * int(ratio * 10)
            lines.append(f"  {ing.name:12s}  {ing.stock:3d}/{ing.max_capacity}  {bar}")
        QMessageBox.information(self, "재고 현황", "\n".join(lines))

    def _show_cash(self) -> None:
        reserve = self._window.change_reserve
        total = reserve.get_total()
        lines = [f"현금 보유량: {total:,}원\n"]
        for denom in sorted(reserve.reserve.keys(), reverse=True):
            lines.append(f"  {denom:,}원권:  {reserve.reserve[denom]}장")
        QMessageBox.information(self, "현금 보유량", "\n".join(lines))

    def _add_cash(self) -> None:
        dlg = _AddCashDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            denomination, count = dlg.result_data
            reserve = self._window.change_reserve
            reserve.add_cash(denomination, count)
            self._window.controller.data_manager.save_change_reserve(
                {str(k): v for k, v in reserve.reserve.items()}
            )
            self._status_label.setText(
                f"현금 추가 완료: {denomination:,}원권 {count}장  "
                f"(보유 총액: {reserve.get_total():,}원)"
            )

    def _change_password(self) -> None:
        from app.password_utils import hash_password
        dlg = _ChangePasswordDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_data:
            hashed = hash_password(dlg.result_data)
            self._window.controller.admin_change_password(hashed)  # 메모리 + 디스크 동시 갱신
            self._status_label.setText("비밀번호가 변경되었습니다.")

    def _shutdown(self) -> None:
        reply = QMessageBox.question(
            self, "종료 확인", "키오스크를 종료하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            sys.exit(0)


class _ToggleProductDialog(QDialog):
    def __init__(self, products: list, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("상품 ON/OFF")
        self.result_data: tuple | None = None

        layout = QVBoxLayout(self)
        self._combo = QComboBox()
        for p in products:
            state = "판매중" if p.is_available else "판매중지"
            self._combo.addItem(f"{p.name}  [{state}]", p.product_id)

        self._state_combo = QComboBox()
        self._state_combo.addItem("판매 중", True)
        self._state_combo.addItem("판매 중지", False)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("확인")
        btn_cancel = QPushButton("취소")
        btn_ok.clicked.connect(self._accept_data)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)

        layout.addWidget(QLabel("상품 선택:"))
        layout.addWidget(self._combo)
        layout.addWidget(QLabel("상태 변경:"))
        layout.addWidget(self._state_combo)
        layout.addLayout(btn_row)

    def _accept_data(self) -> None:
        self.result_data = (self._combo.currentData(), self._state_combo.currentData())
        self.accept()


class _ReplenishDialog(QDialog):
    def __init__(self, ingredients: list, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("재료 보충")
        self.result_data: tuple | None = None
        self._ingredients = ingredients

        layout = QVBoxLayout(self)
        self._combo = QComboBox()
        for ing in ingredients:
            self._combo.addItem(
                f"{ing.name}  ({ing.stock}/{ing.max_capacity}개)", ing.ingredient_id
            )

        self._spin = QSpinBox()
        self._spin.setMinimum(1)
        self._spin.setMaximum(9999)
        self._spin.setValue(10)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("보충")
        btn_cancel = QPushButton("취소")
        btn_ok.clicked.connect(self._accept_data)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)

        layout.addWidget(QLabel("재료 선택:"))
        layout.addWidget(self._combo)
        layout.addWidget(QLabel("보충 수량:"))
        layout.addWidget(self._spin)
        layout.addLayout(btn_row)

    def _accept_data(self) -> None:
        self.result_data = (self._combo.currentData(), self._spin.value())
        self.accept()


class _ChangePasswordDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("비밀번호 변경")
        self.result_data: str = ""

        layout = QVBoxLayout(self)
        self._input = QLineEdit()
        self._input.setPlaceholderText("새 비밀번호")
        self._input.setEchoMode(QLineEdit.EchoMode.Password)
        self._input.returnPressed.connect(self._accept_data)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("변경")
        btn_cancel = QPushButton("취소")
        btn_ok.clicked.connect(self._accept_data)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)

        layout.addWidget(QLabel("새 비밀번호:"))
        layout.addWidget(self._input)
        layout.addLayout(btn_row)

    def _accept_data(self) -> None:
        self.result_data = self._input.text().strip()
        self.accept()


class _AddCashDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("현금 추가")
        self.result_data: tuple[int, int] | None = None

        from app.payment import ChangeReserve
        layout = QVBoxLayout(self)

        self._denom_combo = QComboBox()
        for d in sorted(ChangeReserve.DENOMINATIONS, reverse=True):
            self._denom_combo.addItem(f"{d:,}원권", d)

        self._count_spin = QSpinBox()
        self._count_spin.setMinimum(1)
        self._count_spin.setMaximum(9999)
        self._count_spin.setValue(10)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("추가")
        btn_cancel = QPushButton("취소")
        btn_ok.clicked.connect(self._accept_data)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)

        layout.addWidget(QLabel("권종:"))
        layout.addWidget(self._denom_combo)
        layout.addWidget(QLabel("추가 장수:"))
        layout.addWidget(self._count_spin)
        layout.addLayout(btn_row)

    def _accept_data(self) -> None:
        self.result_data = (self._denom_combo.currentData(), self._count_spin.value())
        self.accept()
