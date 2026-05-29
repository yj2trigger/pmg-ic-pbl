import math
import random

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush
from PyQt6.QtWidgets import QWidget

FLAVOR_COLORS = {
    "vanilla":    QColor(255, 243, 176),
    "choco":      QColor(101,  67,  33),
    "strawberry": QColor(252, 129, 145),
    "mint":       QColor(152, 225, 183),
    "mango":      QColor(255, 179,  71),
}

TOPPING_COLORS = {
    "sprinkle":     [QColor(255,80,80), QColor(80,200,80), QColor(80,80,255), QColor(255,200,0)],
    "nuts":         [QColor(160, 110, 50)],
    "choco_drizzle":[QColor(80, 40, 10)],
}


class StickPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shape = "rect"
        self.color_key = "vanilla"
        self.topping = "none"
        self._topping_positions: list[tuple[float, float]] = []
        self.setMinimumSize(180, 180)

    def update_options(self, shape: str, color_key: str, topping: str) -> None:
        self.shape = shape
        self.color_key = color_key
        self.topping = topping
        if topping != "none":
            rng = random.Random(shape + color_key + topping)
            self._topping_positions = [
                (rng.uniform(0.15, 0.85), rng.uniform(0.08, 0.72))
                for _ in range(22)
            ]
        self.update()

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        color = FLAVOR_COLORS.get(self.color_key, FLAVOR_COLORS["vanilla"])

        body_w = min(w * 0.52, 130)
        body_h = min(h * 0.54, 175)
        body_x = (w - body_w) / 2
        body_y = h * 0.08

        path = self._shape_path(body_x, body_y, body_w, body_h)

        # 막대를 먼저 그려서 아이스크림 바디 아래에 자연스럽게 연결
        stick_w, stick_h = 11, int(h * 0.40)
        stick_x = int((w - stick_w) / 2)

        if self.shape == "star":
            # 별은 하단에 오목한 홈(inner_r) 있음 → inner_r 수준에서 막대 시작
            outer_r = min(body_w, body_h) / 2
            inner_r = outer_r * 0.42
            center_y = body_y + body_h / 2
            stick_y = int(center_y + inner_r * 0.6)  # 오목 홈 위 고체 영역
        else:
            visual_bottom = self._visual_bottom(body_x, body_y, body_w, body_h)
            stick_y = int(visual_bottom - 18)
        painter.setBrush(QBrush(QColor(220, 180, 130)))
        painter.setPen(QPen(QColor(170, 130, 80), 1))
        painter.drawRoundedRect(stick_x, stick_y, stick_w, stick_h, 4, 4)

        # 아이스크림 바디 (막대 위에 덮어서 연결 자연스럽게)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(140), 2))
        painter.drawPath(path)

        if self.topping != "none":
            painter.save()
            painter.setClipPath(path)
            self._draw_toppings(painter, body_x, body_y, body_w, body_h)
            painter.restore()

    def _visual_bottom(self, x, y, w, h) -> float:
        """모양의 실제 시각적 하단 y 좌표 (바운딩박스 하단과 다를 수 있음)."""
        if self.shape == "circle":
            return y + h / 2 + min(w, h) / 2
        if self.shape == "star":
            outer_r = min(w, h) / 2
            return y + h / 2 + outer_r * 0.809  # 5각별 하단 꼭짓점 sin(54°)
        if self.shape == "heart":
            return y + h * 0.88
        return y + h  # rect

    def _shape_path(self, x, y, w, h) -> QPainterPath:
        path = QPainterPath()
        if self.shape == "circle":
            cx, cy = x + w / 2, y + h / 2
            r = min(w, h) / 2
            path.addEllipse(QPointF(cx, cy), r, r)
        elif self.shape == "star":
            r = min(w, h) / 2
            path = _star_path(x + w / 2, y + h / 2, r, r * 0.42, 5)
        elif self.shape == "heart":
            path = _heart_path(x, y, w, h)
        else:
            path.addRoundedRect(x, y, w, h, 14, 14)
        return path

    def _draw_toppings(self, painter: QPainter, bx, by, bw, bh) -> None:
        key = self.topping.replace("top_", "")
        colors = TOPPING_COLORS.get(key, [QColor(255, 0, 0)])
        is_drizzle = key == "choco_drizzle"

        for i, (fx, fy) in enumerate(self._topping_positions):
            px = bx + fx * bw
            py = by + fy * bh
            c = colors[i % len(colors)]
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(c))
            if is_drizzle:
                painter.setPen(QPen(c, 3))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawLine(int(px), int(py), int(px + 22), int(py + 6))
            elif key == "nuts":
                painter.drawEllipse(int(px - 5), int(py - 3), 10, 6)
            else:
                painter.drawEllipse(int(px - 3), int(py - 3), 6, 6)


def _star_path(cx, cy, outer_r, inner_r, points) -> QPainterPath:
    path = QPainterPath()
    step = math.pi / points
    first = True
    for i in range(points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        angle = -math.pi / 2 + i * step
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        if first:
            path.moveTo(px, py)
            first = False
        else:
            path.lineTo(px, py)
    path.closeSubpath()
    return path


def _heart_path(x, y, w, h) -> QPainterPath:
    path = QPainterPath()
    cx = x + w / 2
    top_y = y + h * 0.32
    path.moveTo(cx, y + h * 0.88)
    path.cubicTo(x - w * 0.08, y + h * 0.56, x - w * 0.08, top_y, cx - w * 0.26, top_y)
    path.cubicTo(cx - w * 0.26, y + h * 0.02, cx, y + h * 0.18, cx, top_y)
    path.cubicTo(cx, y + h * 0.18, cx + w * 0.26, y + h * 0.02, cx + w * 0.26, top_y)
    path.cubicTo(cx + w * 0.08, top_y, cx + w * 0.08, y + h * 0.56, cx, y + h * 0.88)
    return path
