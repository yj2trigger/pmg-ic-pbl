# ──────────────────────────────────────────────────────────────────────────────
# scoop_preview.py — 스쿱 아이스크림 실시간 미리보기 커스텀 위젯
#
# [역할]
#   커스터마이즈 화면에서 용기(컵/콘)·스쿱 맛 선택에 따라 즉시 갱신되는 QPainter 위젯.
#
# [핵심 구조]
#   - ScoopPreviewWidget: update_options() 호출 → repaint. 컵/콘 두 가지 용기 지원.
#   - 컵형: 1~3개 스쿱을 입체감 있게 좌/우/앞 배치.
#   - 콘형: 아래에서 위로 스쿱을 20% 겹쳐 쌓음.
#   - 모듈 수준 함수 (_draw_scoop, _draw_cup, _draw_cone): 도형 그리기 전담.
#     ScoopPreviewWidget과 함께 이 파일 안에만 존재. 외부에서 직접 호출하지 않음.
#
# [의존성]
#   import: PyQt6.QtCore, PyQt6.QtGui, PyQt6.QtWidgets
#           app.gui.widgets.colors (FLAVOR_COLORS)
#   이 파일을 사용하는 곳:
#     gui/screens/customize.py → ScoopPreviewWidget() 동적 생성 (스쿱 상품 선택 시)
# ──────────────────────────────────────────────────────────────────────────────

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush
from PyQt6.QtWidgets import QWidget

from app.gui.widgets.colors import FLAVOR_COLORS


class ScoopPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.container = "cup"
        self.scoops: list[str] = []
        self.setMinimumSize(180, 180)

    def update_options(self, container: str, scoops: list[str]) -> None:
        self.container = container
        self.scoops = scoops
        self.update()

    def paintEvent(self, _) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cup_w = min(w * 0.55, 150)
        is_cone = self.container == "cone"
        container_h = min(h * (0.45 if is_cone else 0.30), 140 if is_cone else 90)
        cup_x = (w - cup_w) / 2
        cup_y = h - container_h - h * 0.04
        scoop_r = min(cup_w * 0.52, 55)
        cx = w / 2

        if not is_cone:
            if self.scoops:
                self._draw_cup_scoops(painter, cx, cup_y, scoop_r)
            _draw_cup(painter, cup_x, cup_y, cup_w, container_h)
        else:
            if self.scoops:
                self._draw_cone_scoops(painter, cx, cup_y, scoop_r)
            _draw_cone(painter, cup_x, cup_y, cup_w, container_h)

    def _draw_cup_scoops(self, painter: QPainter, cx: float, cup_y: float, r: float) -> None:
        """컵형: 스쿱을 좌/우/앞 입체 배치"""
        n = len(self.scoops)

        D = 0.12  # 전체 아래로 이동 오프셋 (상대위치 유지)
        if n == 1:
            positions = [(cx, cup_y - r * (0.85 - D), r)]
        elif n == 2:
            positions = [
                (cx - r * 0.58, cup_y - r * (0.85 - D), r * 0.88),
                (cx + r * 0.58, cup_y - r * (0.85 - D), r * 0.88),
            ]
        else:
            positions = [
                (cx - r * 0.58, cup_y - r * (0.68 - D), r * 0.82),  # 뒤-왼쪽
                (cx + r * 0.58, cup_y - r * (0.68 - D), r * 0.82),  # 뒤-오른쪽
                (cx,            cup_y - r * (0.88 - D), r * 0.88),  # 앞-중앙
            ]

        for (sx, sy, sr), flavor in zip(positions, self.scoops):
            _draw_scoop(painter, flavor, sx, sy, sr)

    def _draw_cone_scoops(self, painter: QPainter, cx: float, cup_y: float, r: float) -> None:
        """콘형: 콘 입구에서 시작, 서로 20% 겹쳐서 쌓임. 위 스쿱이 앞(위)에 그려짐."""
        for i, flavor in enumerate(self.scoops):
            # 최하단(i=0) 스쿱 중심이 콘 입구 0.5r 위 → 아래 절반이 콘 안에 들어감
            sy = cup_y - (0.5 + i * 1.2) * r
            _draw_scoop(painter, flavor, cx, sy, r)


def _draw_scoop(painter: QPainter, flavor: str, cx: float, cy: float, r: float) -> None:
    color = FLAVOR_COLORS.get(flavor, QColor(200, 200, 200))
    painter.setBrush(QBrush(color))
    painter.setPen(QPen(color.darker(130), 2))
    painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
    # 광택 하이라이트
    highlight = color.lighter(150)
    highlight.setAlpha(120)
    painter.setBrush(QBrush(highlight))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(int(cx - r * 0.45), int(cy - r * 0.55), int(r * 0.55), int(r * 0.45))


def _draw_cup(painter: QPainter, x, y, w, h) -> None:
    path = QPainterPath()
    path.moveTo(x, y)
    path.lineTo(x + w, y)
    path.lineTo(x + w * 0.84, y + h)
    path.lineTo(x + w * 0.16, y + h)
    path.closeSubpath()
    painter.setBrush(QBrush(QColor(210, 230, 255, 210)))
    painter.setPen(QPen(QColor(160, 180, 220), 2))
    painter.drawPath(path)


def _draw_cone(painter: QPainter, x, y, w, h) -> None:
    path = QPainterPath()
    path.moveTo(x, y)
    path.lineTo(x + w, y)
    path.lineTo(x + w / 2, y + h)
    path.closeSubpath()
    painter.setBrush(QBrush(QColor(240, 195, 125)))
    painter.setPen(QPen(QColor(195, 150, 80), 2))
    painter.drawPath(path)

    painter.setPen(QPen(QColor(195, 150, 80), 1))
    for i in range(1, 5):
        t = i / 5
        lx1 = x * (1 - t) + (x + w / 2) * t
        lx2 = (x + w) * (1 - t) + (x + w / 2) * t
        ly = y + h * t
        painter.drawLine(int(lx1), int(ly), int(lx2), int(ly))
