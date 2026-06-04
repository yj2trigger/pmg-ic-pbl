from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QButtonGroup, QFrame, QSpinBox, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class OptionGroupWidget(QFrame):
    selection_changed = pyqtSignal()

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

        _COLS = 3
        grid = QGridLayout()
        grid.setSpacing(6)
        for i, option in enumerate(group.get_options()):
            price_str = f"  (+{option.extra_price:,}원)" if option.extra_price else ""
            stock_str = "  ※품절" if option.option_id in unavailable else ""
            btn = QPushButton(f"{option.name}{price_str}{stock_str}")
            btn.setCheckable(True)
            btn.setEnabled(option.option_id not in unavailable)
            btn.setProperty("option", option)
            self._btn_group.addButton(btn)
            grid.addWidget(btn, i // _COLS, i % _COLS)
        layout.addLayout(grid)

        self._btn_group.buttonClicked.connect(lambda: self.selection_changed.emit())

    @property
    def group_id(self) -> str:
        return self._group.group_id

    def get_selected_option(self):
        checked = self._btn_group.checkedButton()
        return checked.property("option") if checked else None

    def force_select_option_id(self, option_id: str) -> None:
        for btn in self._btn_group.buttons():
            opt = btn.property("option")
            if opt and opt.option_id == option_id:
                btn.setChecked(True)
                break


class CustomizeScreen(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._product = None
        self._option_widgets: list[OptionGroupWidget] = []
        self._scoop3_widget: OptionGroupWidget | None = None
        self._scoop2_widget: OptionGroupWidget | None = None
        self._preview_widget = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 6, 20, 6)
        outer.setSpacing(6)

        self._title = QLabel()
        self._title.setFont(QFont("Malgun Gothic", 22, QFont.Weight.Bold))
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        body = QHBoxLayout()
        body.setSpacing(20)

        self._options_area = QWidget()
        self._options_layout = QVBoxLayout(self._options_area)
        self._options_layout.setSpacing(10)
        scroll = QScrollArea()
        scroll.setWidget(self._options_area)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(340)
        scroll.setMinimumHeight(0)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._preview_container = QFrame()
        self._preview_container.setMinimumWidth(240)
        self._preview_container.setStyleSheet("background: #2a2a3e; border-radius: 12px;")
        self._preview_layout = QVBoxLayout(self._preview_container)
        self._preview_layout.setContentsMargins(8, 8, 8, 4)
        self._preview_label = QLabel("미리보기")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setFont(QFont("Malgun Gothic", 11))
        self._preview_label.setStyleSheet("color: #6c7086;")
        self._preview_layout.addStretch()
        self._preview_layout.addWidget(self._preview_label)

        body.addWidget(scroll, 3)
        body.addWidget(self._preview_container, 2)

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
        self._qty_spin.valueChanged.connect(self._on_option_changed)
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
        btn_back.clicked.connect(lambda: self._window.go_to_main_menu())
        btn_confirm.clicked.connect(self._confirm)
        btn_row.addWidget(btn_back)
        btn_row.addWidget(btn_confirm)

        outer.addWidget(self._title)
        outer.addLayout(body, 1)
        outer.addLayout(qty_row)
        outer.addWidget(self._error_label)
        outer.addLayout(btn_row)

    def setup(self, product) -> None:
        self._product = product
        self._title.setText(f"{product.get_display_name()}  ({product.base_price:,}원~)")
        self._error_label.setText("")
        self._scoop2_widget = None
        self._scoop3_widget = None

        for w in self._option_widgets:
            w.deleteLater()
        self._option_widgets.clear()
        while self._options_layout.count():
            item = self._options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self._preview_widget:
            self._preview_layout.removeWidget(self._preview_widget)
            self._preview_widget.deleteLater()
            self._preview_widget = None

        if product.product_type == "stick":
            from app.gui.widgets.stick_preview import StickPreviewWidget
            self._preview_widget = StickPreviewWidget()
        else:
            from app.gui.widgets.scoop_preview import ScoopPreviewWidget
            self._preview_widget = ScoopPreviewWidget()

        # stretch(0) + preview_widget(1) + label(2) 순서 유지: widget을 label 위에 삽입
        self._preview_layout.insertWidget(0, self._preview_widget, 1)

        ctrl = self._window.controller
        unavailable = ctrl.get_unavailable_options(product, {})
        for group in ctrl.get_option_groups(product):
            w = OptionGroupWidget(group, unavailable)
            w.selection_changed.connect(self._on_option_changed)
            self._option_widgets.append(w)
            self._options_layout.addWidget(w)
            if group.group_id == "scoop2":
                self._scoop2_widget = w
            if group.group_id == "scoop3":
                self._scoop3_widget = w
        self._options_layout.addStretch()

        if self._scoop3_widget:
            self._scoop3_widget.force_select_option_id("scoop_stop3")

        self._qty_spin.setValue(1)
        self._on_option_changed()

    def _on_option_changed(self) -> None:
        self._update_scoop3_visibility()
        self._update_price()
        self._update_preview()

    def _update_scoop3_visibility(self) -> None:
        if not self._scoop2_widget or not self._scoop3_widget:
            return
        opt2 = self._scoop2_widget.get_selected_option()
        is_stop = opt2 and opt2.option_id == "scoop_stop2"
        self._scoop3_widget.setVisible(not is_stop)
        if is_stop:
            self._scoop3_widget.force_select_option_id("scoop_stop3")

    def _update_price(self) -> None:
        if not self._product:
            return
        selected = self._get_selected_options()
        if selected is None:
            self._price_label.setText("옵션을 모두 선택하세요")
            return
        price = self._product.calculate_price(selected) * self._qty_spin.value()
        self._price_label.setText(f"예상 {price:,}원")

    def _update_preview(self) -> None:
        if not self._preview_widget or not self._product:
            return
        # 부분 선택도 즉시 반영: 선택된 것만 모아서 미리보기 갱신
        partial: dict = {}
        for w in self._option_widgets:
            opt = w.get_selected_option()
            if opt is not None:
                partial[w.group_id] = opt

        ptype = self._product.product_type
        if ptype == "stick":
            shape_opt = partial.get("shape")
            coat_opt = partial.get("coating")
            top_opt = partial.get("topping")
            shape = shape_opt.option_id.replace("shape_", "") if shape_opt else "rect"
            color_key = coat_opt.option_id.replace("coat_", "") if coat_opt else "vanilla"
            topping = top_opt.option_id if top_opt else "none"
            self._preview_widget.update_options(shape, color_key, topping)
        else:
            cont_opt = partial.get("container")
            container = "cone" if (cont_opt and cont_opt.option_id == "cont_cone") else "cup"
            scoops = []
            for slot in ("scoop1", "scoop2", "scoop3"):
                opt = partial.get(slot)
                if opt and not opt.option_id.startswith("scoop_stop"):
                    scoops.append(opt.option_id.split("_", 1)[1])
            self._preview_widget.update_options(container, scoops)

    def _get_selected_options(self, include_hidden: bool = False) -> dict | None:
        selected = {}
        for w in self._option_widgets:
            if not include_hidden and not w.isVisible():
                continue
            opt = w.get_selected_option()
            if opt is None and w.isVisible():
                return None
            if opt is not None:
                selected[w.group_id] = opt
        return selected

    def _confirm(self) -> None:
        self._error_label.setText("")
        selected = self._get_selected_options()
        if selected is None:
            self._error_label.setText("모든 옵션을 선택해 주세요.")
            return

        hidden_scoop3 = (
            self._scoop3_widget is not None
            and not self._scoop3_widget.isVisible()
        )
        if hidden_scoop3:
            stop3 = next(
                (o for o in self._scoop3_widget._group.get_options()
                 if o.option_id == "scoop_stop3"),
                None,
            )
            if stop3:
                selected["scoop3"] = stop3

        try:
            self._window.controller.add_to_cart(
                self._product, selected, self._qty_spin.value()
            )
            self._window.go_to_main_menu()
        except Exception as e:
            self._error_label.setText(f"오류: {e}")
