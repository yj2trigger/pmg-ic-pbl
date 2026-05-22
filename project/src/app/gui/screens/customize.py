from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QButtonGroup, QFrame, QSpinBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class OptionGroupWidget(QFrame):
    """한 옵션 그룹을 exclusive 토글버튼으로 표시."""

    def __init__(self, group, unavailable: set) -> None:
        super().__init__()
        self._group = group
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        title = QLabel(f"[ {group.name} ]")
        title.setFont(QFont("Malgun Gothic", 15, QFont.Weight.Bold))
        layout.addWidget(title)

        row = QHBoxLayout()
        for option in group.get_options():
            price_str = f"  (+{option.extra_price:,}원)" if option.extra_price else ""
            stock_str = "  ※품절" if option.option_id in unavailable else ""
            btn = QPushButton(f"{option.name}{price_str}{stock_str}")
            btn.setCheckable(True)
            btn.setEnabled(option.option_id not in unavailable)
            btn.setProperty("option", option)
            self._btn_group.addButton(btn)
            row.addWidget(btn)
        layout.addLayout(row)

    @property
    def group_id(self) -> str:
        return self._group.group_id

    def get_selected_option(self):
        checked = self._btn_group.checkedButton()
        return checked.property("option") if checked else None


class CustomizeScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._product = None
        self._option_widgets: list[OptionGroupWidget] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(12)

        self._title = QLabel()
        self._title.setFont(QFont("Malgun Gothic", 22, QFont.Weight.Bold))
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._options_area = QWidget()
        self._options_layout = QVBoxLayout(self._options_area)
        self._options_layout.setSpacing(10)
        scroll = QScrollArea()
        scroll.setWidget(self._options_area)
        scroll.setWidgetResizable(True)

        # Quantity + live price
        qty_row = QHBoxLayout()
        qty_label = QLabel("수량:")
        qty_label.setFont(QFont("Malgun Gothic", 15))
        self._qty_spin = QSpinBox()
        self._qty_spin.setMinimum(1)
        self._qty_spin.setMaximum(99)
        self._qty_spin.setFont(QFont("Malgun Gothic", 15))
        self._qty_spin.setMinimumWidth(80)
        self._price_label = QLabel()
        self._price_label.setFont(QFont("Malgun Gothic", 17, QFont.Weight.Bold))
        self._price_label.setStyleSheet("color: #a6e3a1;")
        self._qty_spin.valueChanged.connect(self._update_price)
        qty_row.addWidget(qty_label)
        qty_row.addWidget(self._qty_spin)
        qty_row.addStretch()
        qty_row.addWidget(self._price_label)

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: #f38ba8;")
        self._error_label.setFont(QFont("Malgun Gothic", 13))

        btn_row = QHBoxLayout()
        btn_back = QPushButton("←  뒤로")
        btn_confirm = QPushButton("장바구니에 추가  →")
        btn_back.setMinimumHeight(56)
        btn_confirm.setMinimumHeight(56)
        btn_back.clicked.connect(self._go_back)
        btn_confirm.clicked.connect(self._confirm)
        btn_row.addWidget(btn_back)
        btn_row.addWidget(btn_confirm)

        layout.addWidget(self._title)
        layout.addWidget(scroll, 1)
        layout.addLayout(qty_row)
        layout.addWidget(self._error_label)
        layout.addLayout(btn_row)

    def setup(self, product) -> None:
        self._product = product
        self._title.setText(f"{product.get_display_name()}  ({product.base_price:,}원~)")
        self._error_label.setText("")

        for w in self._option_widgets:
            w.deleteLater()
        self._option_widgets.clear()
        while self._options_layout.count():
            item = self._options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        ctrl = self._window.controller
        unavailable = ctrl.get_unavailable_options(product, {})
        for group in ctrl.get_option_groups(product):
            w = OptionGroupWidget(group, unavailable)
            self._option_widgets.append(w)
            self._options_layout.addWidget(w)
        self._options_layout.addStretch()

        self._qty_spin.setValue(1)
        self._update_price()

    def _get_selected_options(self) -> dict | None:
        selected = {}
        for w in self._option_widgets:
            opt = w.get_selected_option()
            if opt is None:
                return None
            selected[w.group_id] = opt
        return selected

    def _update_price(self) -> None:
        if not self._product:
            return
        selected = self._get_selected_options()
        if selected is None:
            self._price_label.setText("옵션을 모두 선택하세요")
            return
        price = self._product.calculate_price(selected) * self._qty_spin.value()
        self._price_label.setText(f"예상 {price:,}원")

    def _confirm(self) -> None:
        self._error_label.setText("")
        selected = self._get_selected_options()
        if selected is None:
            self._error_label.setText("모든 옵션을 선택해 주세요.")
            return
        try:
            self._window.controller.add_to_cart(
                self._product, selected, self._qty_spin.value()
            )
            self._window.go_to_main_menu()
        except Exception as e:
            self._error_label.setText(f"오류: {e}")

    def _go_back(self) -> None:
        ptype = self._product.product_type if self._product else "coffee"
        self._window.go_to_product_list(ptype)
