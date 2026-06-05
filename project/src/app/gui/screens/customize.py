# ──────────────────────────────────────────────────────────────────────────────
# gui/screens/customize.py — 옵션 커스터마이징 화면 (가장 복잡한 화면)
#
# [역할]
#   사용자가 아이스크림 옵션(모양/코팅/토핑/용기/맛)을 선택하는 화면이다.
#   선택할 때마다 오른쪽 미리보기가 즉시 갱신되고, 예상 가격이 업데이트된다.
#
# [핵심 구조]
#   왼쪽: 옵션 그룹들 (QScrollArea 안에 OptionGroupWidget 목록)
#   오른쪽: 미리보기 위젯 (StickPreviewWidget 또는 ScoopPreviewWidget)
#
# [스쿱 2/3번째 슬롯 특수 처리]
#   스쿱은 1~3개를 고를 수 있다. scoop2 그룹에서 "여기서 그만" 옵션을 선택하면
#   scoop3 그룹을 숨긴다. scoop3은 숨겨져도 내부적으로 "scoop_stop3" 옵션으로 설정된다.
#   장바구니에 담을 때 숨겨진 scoop3에 stop3 옵션을 자동으로 주입한다 (_confirm 참고).
#
# [의존성]
#   import: PyQt6 위젯들
#   사용하는 객체: kiosk_controller.get_option_groups(), get_unavailable_options(), add_to_cart()
#   생성하는 위젯: OptionGroupWidget, StickPreviewWidget, ScoopPreviewWidget
# ──────────────────────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QButtonGroup, QFrame, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class OptionGroupWidget(QFrame):
    # 하나의 옵션 그룹(예: "코팅 선택")을 나타내는 위젯.
    # 그룹 내 옵션 버튼들은 QButtonGroup으로 묶어서 한 번에 하나만 선택되도록 한다.

    # 선택이 바뀌면 emit되는 시그널. CustomizeScreen이 이 시그널을 받아서 미리보기를 갱신한다.
    selection_changed = pyqtSignal()

    def __init__(self, group, unavailable: set) -> None:
        super().__init__()
        self._group = group
        # QButtonGroup(exclusive=True): 같은 그룹 내에서 하나의 버튼만 체크 상태가 된다.
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        title = QLabel(f"[ {group.name} ]")
        title.setFont(QFont("Malgun Gothic", 15, QFont.Weight.Bold))
        layout.addWidget(title)

        # 옵션 버튼을 3열 그리드로 배치한다. (버튼이 많아도 정렬이 깔끔하게 유지됨)
        _COLS = 3
        grid = QGridLayout()
        grid.setSpacing(6)
        for i, option in enumerate(group.get_options()):
            # 추가 금액이 있으면 버튼 텍스트에 표시
            price_str = f"  (+{option.extra_price:,}원)" if option.extra_price else ""
            # 재고 없는 옵션에는 "※품절" 표시
            stock_str = "  ※품절" if option.option_id in unavailable else ""
            btn = QPushButton(f"{option.name}{price_str}{stock_str}")
            btn.setCheckable(True)               # 체크 가능한 토글 버튼
            btn.setEnabled(option.option_id not in unavailable)  # 품절이면 비활성화
            # btn에 option 객체 자체를 저장한다. get_selected_option()에서 꺼내 쓴다.
            btn.setProperty("option", option)
            self._btn_group.addButton(btn)
            grid.addWidget(btn, i // _COLS, i % _COLS)
        layout.addLayout(grid)

        # 버튼 클릭 시 selection_changed 시그널을 emit한다.
        self._btn_group.buttonClicked.connect(lambda: self.selection_changed.emit())

    @property
    def group_id(self) -> str:
        # 이 위젯이 나타내는 옵션 그룹의 ID를 반환한다.
        return self._group.group_id

    def get_selected_option(self):
        # 현재 선택된 버튼의 option 객체를 반환한다.
        # 아무것도 선택 안 됐으면 None 반환.
        checked = self._btn_group.checkedButton()
        return checked.property("option") if checked else None

    def force_select_option_id(self, option_id: str) -> None:
        # 특정 option_id를 가진 버튼을 강제로 선택 상태로 만든다.
        # 사용처: scoop3 그룹에서 "scoop_stop3"를 기본 선택으로 설정할 때.
        for btn in self._btn_group.buttons():
            opt = btn.property("option")
            if opt and opt.option_id == option_id:
                btn.setChecked(True)
                break


class CustomizeScreen(QWidget):
    # 옵션 커스터마이징 화면. 상품 하나를 선택한 후 이 화면에서 옵션을 고른다.

    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        self._product = None                      # 현재 커스터마이징 중인 상품
        self._option_widgets: list[OptionGroupWidget] = []
        self._scoop3_widget: OptionGroupWidget | None = None  # scoop3 그룹 (숨김 제어)
        self._scoop2_widget: OptionGroupWidget | None = None  # scoop2 그룹 (stop2 감지)
        self._preview_widget = None               # 현재 미리보기 위젯
        self._setup_ui()

    def _setup_ui(self) -> None:
        # UI 뼈대 구성. 내용(옵션 그룹)은 setup()에서 동적으로 채운다.
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 6, 20, 6)
        outer.setSpacing(6)

        self._title = QLabel()
        self._title.setFont(QFont("Malgun Gothic", 22, QFont.Weight.Bold))
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # body: 좌(옵션 목록) + 우(미리보기) 2열 레이아웃
        body = QHBoxLayout()
        body.setSpacing(20)

        # 옵션 목록 영역 (스크롤 가능)
        self._options_area = QWidget()
        self._options_layout = QVBoxLayout(self._options_area)
        self._options_layout.setSpacing(10)
        self._scroll = QScrollArea()
        self._scroll.setWidget(self._options_area)
        self._scroll.setWidgetResizable(True)
        self._scroll.setMinimumWidth(340)
        self._scroll.setMinimumHeight(0)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 미리보기 컨테이너 (실제 미리보기 위젯은 setup()에서 삽입)
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

        body.addWidget(self._scroll, 3)           # 좌 3 비율
        body.addWidget(self._preview_container, 2) # 우 2 비율

        # 수량 선택 행
        # QSpinBox 대신 -/+ QPushButton으로 구현: 터치스크린에서 서브버튼 클릭 영역 불일치 버그 방지
        qty_row = QHBoxLayout()
        qty_label = QLabel("수량:")
        qty_label.setFont(QFont("Malgun Gothic", 15))
        self._qty_value = 1
        btn_minus = QPushButton("-")
        btn_plus  = QPushButton("+")
        for b in (btn_minus, btn_plus):
            # padding 재정의: 글로벌 스타일시트 padding:10px 20px이 44px 버튼에 적용되면
            # 텍스트 영역(44-40=4px)이 사라져 문자가 뭉개짐
            b.setStyleSheet("padding: 2px; font-size: 20px; font-weight: bold;")
            b.setFixedSize(44, 44)
        self._qty_label = QLabel("1")
        self._qty_label.setFont(QFont("Malgun Gothic", 15))
        self._qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qty_label.setMinimumWidth(40)
        btn_minus.clicked.connect(self._qty_decrease)
        btn_plus.clicked.connect(self._qty_increase)
        self._price_label = QLabel()
        self._price_label.setFont(QFont("Malgun Gothic", 17, QFont.Weight.Bold))
        self._price_label.setStyleSheet("color: #a6e3a1;")
        qty_row.addWidget(qty_label)
        qty_row.addWidget(btn_minus)
        qty_row.addWidget(self._qty_label)
        qty_row.addWidget(btn_plus)
        qty_row.addStretch()
        qty_row.addWidget(self._price_label)

        # 오류 표시 라벨 (모든 옵션을 선택하지 않고 확인 버튼을 눌렀을 때)
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: #f38ba8;")
        self._error_label.setFont(QFont("Malgun Gothic", 13))

        # 하단 버튼 행
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
        # 상품이 선택되면 그 상품에 맞는 옵션 그룹 위젯들을 동적으로 생성한다.
        # main_window.go_to_customize(product)에서 호출된다.

        # 스크롤 위치를 맨 위로 초기화 (이전 상품 선택 시 스크롤 위치가 남을 수 있음)
        self._scroll.verticalScrollBar().setValue(0)
        self._product = product
        self._title.setText(f"{product.get_display_name()}  ({product.base_price:,}원~)")
        self._error_label.setText("")
        self._scoop2_widget = None
        self._scoop3_widget = None

        # 이전 옵션 위젯들 정리
        for w in self._option_widgets:
            w.deleteLater()
        self._option_widgets.clear()
        while self._options_layout.count():
            item = self._options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 이전 미리보기 위젯 정리 후 새 위젯 생성
        if self._preview_widget:
            self._preview_layout.removeWidget(self._preview_widget)
            self._preview_widget.deleteLater()
            self._preview_widget = None

        # 상품 타입에 따라 미리보기 위젯 종류 결정
        if product.product_type == "stick":
            from app.gui.widgets.stick_preview import StickPreviewWidget
            self._preview_widget = StickPreviewWidget()
        else:
            from app.gui.widgets.scoop_preview import ScoopPreviewWidget
            self._preview_widget = ScoopPreviewWidget()

        # 미리보기 위젯을 레이아웃 인덱스 0에 삽입 (stretch 위에, label 아래에 위치)
        # stretch(index 0) + preview_widget(index 1) + label(index 2) 순서가 된다.
        self._preview_layout.insertWidget(0, self._preview_widget, 1)

        # 이 상품에 맞는 옵션 그룹 위젯 생성
        ctrl = self._window.controller
        unavailable = ctrl.get_unavailable_options(product, {})   # 재고 없는 옵션 ID 집합
        for group in ctrl.get_option_groups(product):
            w = OptionGroupWidget(group, unavailable)
            w.selection_changed.connect(self._on_option_changed)
            self._option_widgets.append(w)
            self._options_layout.addWidget(w)
            # scoop2, scoop3 위젯을 따로 저장해서 숨김 로직에 사용
            if group.group_id == "scoop2":
                self._scoop2_widget = w
            if group.group_id == "scoop3":
                self._scoop3_widget = w
        self._options_layout.addStretch()

        # scoop3가 있으면 처음에 "여기서 그만" 옵션을 기본 선택
        if self._scoop3_widget:
            self._scoop3_widget.force_select_option_id("scoop_stop3")

        self._qty_value = 1
        self._qty_label.setText("1")
        self._on_option_changed()

    def _qty_decrease(self) -> None:
        if self._qty_value > 1:
            self._qty_value -= 1
            self._qty_label.setText(str(self._qty_value))
            self._on_option_changed()

    def _qty_increase(self) -> None:
        if self._qty_value < 99:
            self._qty_value += 1
            self._qty_label.setText(str(self._qty_value))
            self._on_option_changed()

    def _on_option_changed(self) -> None:
        # 옵션 선택 또는 수량이 바뀔 때마다 호출된다.
        # 세 가지를 순서대로 갱신한다.
        self._update_scoop3_visibility()
        self._update_price()
        self._update_preview()

    def _update_scoop3_visibility(self) -> None:
        # scoop2에서 "여기서 그만(scoop_stop2)"을 선택하면 scoop3 위젯을 숨긴다.
        if not self._scoop2_widget or not self._scoop3_widget:
            return
        opt2 = self._scoop2_widget.get_selected_option()
        is_stop = opt2 and opt2.option_id == "scoop_stop2"
        self._scoop3_widget.setVisible(not is_stop)
        if is_stop:
            # 숨기면서 내부적으로 scoop_stop3를 선택 상태로 만든다.
            # _confirm()에서 숨겨진 scoop3에 stop3를 주입할 때 사용.
            self._scoop3_widget.force_select_option_id("scoop_stop3")

    def _update_price(self) -> None:
        # 현재 선택된 옵션 조합의 예상 가격을 계산해서 표시한다.
        if not self._product:
            return
        selected = self._get_selected_options()
        if selected is None:
            # 아직 선택 안 된 옵션이 있는 경우
            self._price_label.setText("옵션을 모두 선택하세요")
            return
        price = self._product.calculate_price(selected) * self._qty_value
        self._price_label.setText(f"예상 {price:,}원")

    def _update_preview(self) -> None:
        # 현재 선택된 옵션으로 미리보기 위젯을 갱신한다.
        # 부분 선택 상태에서도 즉시 반영한다 (선택된 것만 골라서 넘김).
        if not self._preview_widget or not self._product:
            return

        partial: dict = {}
        for w in self._option_widgets:
            opt = w.get_selected_option()
            if opt is not None:
                partial[w.group_id] = opt

        ptype = self._product.product_type
        if ptype == "stick":
            # stick: shape / coating / topping 옵션에서 option_id 파싱
            shape_opt = partial.get("shape")
            coat_opt = partial.get("coating")
            top_opt = partial.get("topping")
            # option_id에서 그룹 접두사 제거: "shape_rect" → "rect"
            shape = shape_opt.option_id.replace("shape_", "") if shape_opt else "rect"
            color_key = coat_opt.option_id.replace("coat_", "") if coat_opt else "vanilla"
            topping = top_opt.option_id if top_opt else "none"
            self._preview_widget.update_options(shape, color_key, topping)
        else:
            # scoop: container / scoop1 / scoop2 / scoop3 옵션에서 파싱
            cont_opt = partial.get("container")
            container = "cone" if (cont_opt and cont_opt.option_id == "cont_cone") else "cup"
            scoops = []
            for slot in ("scoop1", "scoop2", "scoop3"):
                opt = partial.get(slot)
                # scoop_stop으로 시작하는 옵션은 "그만"을 의미하므로 제외
                if opt and not opt.option_id.startswith("scoop_stop"):
                    # "flavor_vanilla" → "vanilla" (접두사 제거)
                    scoops.append(opt.option_id.split("_", 1)[1])
            self._preview_widget.update_options(container, scoops)

    def _get_selected_options(self) -> dict | None:
        # 현재 보이는 옵션 그룹의 선택값을 {group_id: Option} 딕셔너리로 반환한다.
        # 숨겨진 그룹(scoop3 등)은 항상 제외한다 — 별도 주입은 _confirm()에서 처리.
        # 선택 안 된 보이는 그룹이 있으면 None 반환 (미완성 선택 표시).
        selected = {}
        for w in self._option_widgets:
            if not w.isVisible():
                continue   # 숨겨진 그룹 건너뜀 (scoop3 등)
            opt = w.get_selected_option()
            if opt is None:
                return None   # 보이는 그룹에서 아무것도 안 선택됨
            selected[w.group_id] = opt
        return selected

    def _confirm(self) -> None:
        # "장바구니에 추가" 버튼을 눌렀을 때 호출된다.
        self._error_label.setText("")
        selected = self._get_selected_options()
        if selected is None:
            self._error_label.setText("모든 옵션을 선택해 주세요.")
            return

        # 숨겨진 scoop3가 있으면 stop3 옵션을 selected에 자동 주입한다.
        # 왜 필요한가?
        #   scoop3 위젯이 숨겨져 있으면 _get_selected_options()에서 제외되지만,
        #   OrderItem.get_required_ingredients()는 selected_options의 모든 옵션을 순회하므로
        #   scoop3에 대한 재료 소비가 0이 되도록 stop3 옵션을 명시해야 한다.
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
            # 장바구니에 추가 (재고 차감 포함)
            self._window.controller.add_to_cart(
                self._product, selected, self._qty_value
            )
            self._window.go_to_main_menu()
        except Exception as e:
            # InsufficientStockException 등 예외 발생 시 화면에 표시
            self._error_label.setText(f"오류: {e}")
