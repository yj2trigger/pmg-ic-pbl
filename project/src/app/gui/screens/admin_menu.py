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
            ("의약품 ON/OFF", self._toggle_medicine),
            ("의약품 가격 변경", self._set_medicine_price),
            ("현금 보유량 확인", self._show_cash),
            ("현금 추가", self._add_cash),
            ("비밀번호 변경", self._change_password),
            ("키오스크 종료", self._shutdown),
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

        btn_back = QPushButton("← 관리자 메뉴 종료")
        btn_back.setMinimumHeight(52)
        btn_back.clicked.connect(lambda: self._window.go_to_symptom_select())

        layout.addWidget(title)
        layout.addLayout(grid)
        layout.addWidget(self._status_label)
        layout.addStretch()
        layout.addWidget(btn_back)

    def refresh(self) -> None:
        self._status_label.setText("")

    # ── Operations ──────────────────────────────────────────────

    def _toggle_medicine(self) -> None:
        ctrl = self._window.controller
        medicines = ctrl._dm.load_medicines()
        dlg = _ToggleMedicineDialog(medicines, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            mid, flag = dlg.result_data
            medicines = ctrl._dm.load_medicines()
            for m in medicines:
                if m.medicine_id == mid:
                    m.is_available = flag
                    break
            ctrl._dm.save_medicines(medicines)
            state = "판매 중" if flag else "판매 중지"
            self._status_label.setText(f"변경 완료:  {mid}  →  {state}")

    def _set_medicine_price(self) -> None:
        ctrl = self._window.controller
        medicines = ctrl._dm.load_medicines()
        dlg = _SetMedicinePriceDialog(medicines, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            mid, price = dlg.result_data
            medicines = ctrl._dm.load_medicines()
            for m in medicines:
                if m.medicine_id == mid:
                    m.base_price = price
                    break
            ctrl._dm.save_medicines(medicines)
            self._status_label.setText(f"가격 변경 완료:  {mid}  →  {price:,}원")

    def _show_cash(self) -> None:
        reserve = self._window.change_reserve
        total = reserve.get_total()
        lines = [f"현금 보유량: {total:,}원", ""]
        for denom in sorted(reserve.reserve.keys(), reverse=True):
            lines.append(f"  {denom:,}원권:  {reserve.reserve[denom]}장")
        QMessageBox.information(self, "현금 보유량", "\n".join(lines))

    def _add_cash(self) -> None:
        dlg = _AddCashDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            denomination, count = dlg.result_data
            reserve = self._window.change_reserve
            reserve.add_cash(denomination, count)
            self._window.controller._dm.save_change_reserve(
                {str(k): v for k, v in reserve.reserve.items()}
            )
            self._status_label.setText(
                f"현금 추가 완료:  {denomination:,}원권  {count}장  "
                f"(보유 총액: {reserve.get_total():,}원)"
            )

    def _change_password(self) -> None:
        dlg = _ChangePasswordDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_data:
            self._window.controller._dm.save_admin_config({"password": dlg.result_data})
            self._status_label.setText("비밀번호가 변경되었습니다.")

    def _shutdown(self) -> None:
        reply = QMessageBox.question(
            self,
            "종료 확인",
            "키오스크를 종료하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            sys.exit(0)


# ── Helper dialogs ────────────────────────────────────────────

class _ToggleMedicineDialog(QDialog):
    def __init__(self, medicines: list, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("의약품 ON/OFF")
        self.result_data: tuple | None = None
        self._medicines = medicines

        layout = QVBoxLayout(self)
        self._combo = QComboBox()
        for m in medicines:
            state = "판매중" if m.is_available else "판매중지"
            self._combo.addItem(f"{m.name}  [{state}]", m.medicine_id)

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

        layout.addWidget(QLabel("의약품 선택:"))
        layout.addWidget(self._combo)
        layout.addWidget(QLabel("상태 변경:"))
        layout.addWidget(self._state_combo)
        layout.addLayout(btn_row)

    def _accept_data(self) -> None:
        self.result_data = (
            self._combo.currentData(),
            self._state_combo.currentData(),
        )
        self.accept()


class _SetMedicinePriceDialog(QDialog):
    def __init__(self, medicines: list, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("의약품 가격 변경")
        self.result_data: tuple | None = None
        self._medicines = medicines

        layout = QVBoxLayout(self)
        self._combo = QComboBox()
        for m in medicines:
            self._combo.addItem(f"{m.name}  ({m.base_price:,}원)", m.medicine_id)
        self._combo.currentIndexChanged.connect(self._update_spin)

        self._spin = QSpinBox()
        self._spin.setMinimum(0)
        self._spin.setMaximum(999_999)
        self._spin.setSingleStep(100)
        self._update_spin()

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("확인")
        btn_cancel = QPushButton("취소")
        btn_ok.clicked.connect(self._accept_data)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)

        layout.addWidget(QLabel("의약품 선택:"))
        layout.addWidget(self._combo)
        layout.addWidget(QLabel("새 가격 (원):"))
        layout.addWidget(self._spin)
        layout.addLayout(btn_row)

    def _update_spin(self) -> None:
        idx = self._combo.currentIndex()
        if 0 <= idx < len(self._medicines):
            self._spin.setValue(self._medicines[idx].base_price)

    def _accept_data(self) -> None:
        idx = self._combo.currentIndex()
        self.result_data = (self._medicines[idx].medicine_id, self._spin.value())
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
        self.result_data = (
            self._denom_combo.currentData(),
            self._count_spin.value(),
        )
        self.accept()
