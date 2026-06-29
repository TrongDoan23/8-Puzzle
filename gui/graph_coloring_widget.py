from __future__ import annotations
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont,
    QLinearGradient,
)

from algorithms.graph_coloring import (
    GraphDefinition, UNASSIGNED, COLOR_PALETTE, NUM_COLORS,
)

NODE_RADIUS = 26

LIGHT_PAL = {
    "bg":            QColor("#F0F4F8"),
    "edge":          QColor("#B0BCCC"),
    "node_empty":    QColor("#DDE6F0"),
    "node_border":   QColor("#8090A4"),
    "node_conflict": QColor("#F5A623"),
    "node_selected": QColor("#FFFFFF"),
    "text":          QColor("#1A2332"),
    "shadow":        QColor(0, 0, 0, 28),
    "sel_ring":      QColor("#F5A623"),
}
DARK_PAL = {
    "bg":            QColor("#1A2332"),
    "edge":          QColor("#354A60"),
    "node_empty":    QColor("#2A3A50"),
    "node_border":   QColor("#5A7090"),
    "node_conflict": QColor("#D4911F"),
    "node_selected": QColor("#3A5070"),
    "text":          QColor("#E8EDF2"),
    "shadow":        QColor(0, 0, 0, 55),
    "sel_ring":      QColor("#F5A623"),
}


class GraphColoringWidget(QWidget):
    """
    Draws a graph and lets users click nodes to color them.
    Emits node_clicked(node_idx) when the user clicks a node.
    """

    node_clicked = pyqtSignal(int)   # user clicked this node index

    def __init__(self, parent=None, dark: bool = False) -> None:
        super().__init__(parent)
        self._dark = dark
        self._graph: Optional[GraphDefinition] = None
        self._assignment: List[int] = []
        self._highlighted: int = -1       # last step highlight
        self._conflict_nodes: List[int] = []
        self._selected: int = -1          # user-selected node

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(280, 240)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    # ── Public API ────────────────────────────────────────────────────

    def set_dark(self, dark: bool) -> None:
        self._dark = dark
        self.update()

    def set_graph(self, graph: GraphDefinition) -> None:
        self._graph = graph
        self._assignment = [UNASSIGNED] * graph.num_nodes
        self._highlighted = -1
        self._conflict_nodes = []
        self._selected = -1
        self.update()

    def reset(self) -> None:
        if self._graph:
            self._assignment = [UNASSIGNED] * self._graph.num_nodes
        self._highlighted = -1
        self._conflict_nodes = []
        self._selected = -1
        self.update()

    def apply_step(self, action: str, node: int, color: int) -> None:
        """Apply one algorithm animation step."""
        self._conflict_nodes = []
        self._selected = -1
        if action == "assign":
            self._assignment[node] = color
            self._highlighted = node
        elif action == "unassign":
            self._assignment[node] = UNASSIGNED
            self._highlighted = node
        elif action == "conflict":
            self._conflict_nodes = [node]
            self._highlighted = node
        self.update()

    def paint_selected(self, color_idx: int) -> None:
        """Paint the currently selected node with color_idx."""
        if self._selected >= 0:
            self._assignment[self._selected] = color_idx
            self._selected = -1
            self.update()

    def get_selected_node(self) -> int:
        return self._selected

    def get_assignment(self) -> List[int]:
        return self._assignment[:]

    def has_conflicts(self) -> bool:
        if not self._graph:
            return False
        for a, b in self._graph.edges:
            if (self._assignment[a] != UNASSIGNED and
                    self._assignment[a] == self._assignment[b]):
                return True
        return False

    def is_complete(self) -> bool:
        return (self._graph is not None and
                all(c != UNASSIGNED for c in self._assignment))

    # ── Geometry ──────────────────────────────────────────────────────

    def _node_pos(self, idx: int) -> QPointF:
        if not self._graph:
            return QPointF(0, 0)
        nx, ny = self._graph.positions[idx]
        return QPointF(nx * self.width(), ny * self.height())

    def _node_at(self, x: float, y: float) -> int:
        if not self._graph:
            return -1
        for i in range(self._graph.num_nodes):
            pos = self._node_pos(i)
            dx, dy = x - pos.x(), y - pos.y()
            if dx * dx + dy * dy <= (NODE_RADIUS + 4) ** 2:
                return i
        return -1

    # ── Mouse events ──────────────────────────────────────────────────

    def mousePressEvent(self, ev) -> None:  # type: ignore[override]
        if ev.button() == Qt.MouseButton.LeftButton and self._graph:
            idx = self._node_at(ev.position().x(), ev.position().y())
            if idx >= 0:
                self._selected = idx if self._selected != idx else -1
                self.update()
                if self._selected >= 0:
                    self.node_clicked.emit(idx)

    def resizeEvent(self, ev) -> None:  # type: ignore[override]
        super().resizeEvent(ev)
        self.update()

    # ── Painting ──────────────────────────────────────────────────────

    def paintEvent(self, _ev) -> None:  # type: ignore[override]
        if not self._graph:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = DARK_PAL if self._dark else LIGHT_PAL

        p.fillRect(self.rect(), pal["bg"])

        # Conflict edges (red highlight)
        conflict_edges = set()
        if self._graph:
            for a, b in self._graph.edges:
                if (self._assignment[a] != UNASSIGNED and
                        self._assignment[a] == self._assignment[b]):
                    conflict_edges.add((a, b))

        # Draw edges
        for a, b in self._graph.edges:
            pa, pb = self._node_pos(a), self._node_pos(b)
            if (a, b) in conflict_edges or (b, a) in conflict_edges:
                p.setPen(QPen(QColor("#E05555"), 3))
            else:
                p.setPen(QPen(pal["edge"], 2))
            p.drawLine(pa, pb)

        # Draw nodes
        for i in range(self._graph.num_nodes):
            self._draw_node(p, i, pal)

        p.end()

    def _draw_node(self, p: QPainter, idx: int, pal: dict) -> None:
        pos  = self._node_pos(idx)
        r    = NODE_RADIUS
        rect = QRectF(pos.x() - r, pos.y() - r, r * 2, r * 2)

        # Shadow
        p.setBrush(QBrush(pal["shadow"]))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(rect.adjusted(2, 3, 2, 3))

        color      = self._assignment[idx]
        in_conflict = idx in self._conflict_nodes
        is_sel      = idx == self._selected
        is_hi       = idx == self._highlighted

        if in_conflict:
            fill = QColor(pal["node_conflict"])
        elif color == UNASSIGNED:
            fill = QColor(pal["node_selected"] if is_sel else pal["node_empty"])
        else:
            fill = QColor(COLOR_PALETTE[color])

        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, fill.lighter(118))
        grad.setColorAt(1.0, fill)
        p.setBrush(QBrush(grad))

        # Border
        if is_sel:
            pen = QPen(pal["sel_ring"], 3)
        elif is_hi and not in_conflict:
            pen = QPen(QColor("#F5A623"), 2)
        elif color != UNASSIGNED and not in_conflict:
            pen = QPen(QColor(fill).darker(130), 2)
        else:
            pen = QPen(pal["node_border"], 1.5)
        p.setPen(pen)
        p.drawEllipse(rect)

        # Label
        p.setPen(QPen(pal["text"]))
        p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter,
                   self._graph.names[idx])  # type: ignore[union-attr]
