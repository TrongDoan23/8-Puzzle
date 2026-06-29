from __future__ import annotations
from typing import List, Optional, Callable

from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import (
    Qt, QRect, QRectF, QPointF, QTimer, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QLineF
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QPainterPath,
    QLinearGradient, QBrush, QRadialGradient
)

from algorithms.minimax import WINNING_LINES, _check_winner


# ── Colour palettes ──────────────────────────────────────────────────────

LIGHT = {
    "bg":          QColor("#F0F4F8"),
    "panel":       QColor("#FFFFFF"),
    "grid":        QColor("#C0CCDA"),
    "cell_hover":  QColor("#E8F0FA"),
    "cell_bg":     QColor("#F7FAFC"),
    "x_color":     QColor("#E05555"),
    "x_shadow":    QColor(224, 85, 85, 50),
    "o_color":     QColor("#4A90D9"),
    "o_shadow":    QColor(74, 144, 217, 50),
    "win_line":    QColor("#44B87A"),
    "win_bg":      QColor(68, 184, 122, 30),
    "draw_bg":     QColor(150, 150, 150, 30),
}

DARK = {
    "bg":          QColor("#1A2332"),
    "panel":       QColor("#243040"),
    "grid":        QColor("#354A60"),
    "cell_hover":  QColor("#2A3C54"),
    "cell_bg":     QColor("#1E2A3A"),
    "x_color":     QColor("#E06060"),
    "x_shadow":    QColor(224, 96, 96, 60),
    "o_color":     QColor("#5AA0E8"),
    "o_shadow":    QColor(90, 160, 232, 60),
    "win_line":    QColor("#44D880"),
    "win_bg":      QColor(68, 216, 128, 25),
    "draw_bg":     QColor(120, 120, 120, 25),
}

CORNER = 12
PAD    = 20
GAP    = 8


class TicTacToeWidget(QWidget):
    """
    3×3 Tic-Tac-Toe board.

    Signals
    -------
    cell_clicked(int)  — emitted when a human clicks an empty cell (0-8)
    """

    cell_clicked = pyqtSignal(int)

    def __init__(self, parent=None, dark: bool = False) -> None:
        super().__init__(parent)
        self._dark = dark
        # 0 = empty, 1 = X (human), 2 = O (AI)
        self._board: List[int] = [0] * 9
        self._hovered: int = -1
        self._human_turn: bool = True
        self._game_over: bool = False
        self._winner: int = 0       # 0=none/draw, 1=X, 2=O
        self._win_line: Optional[tuple] = None  # (a,b,c) indices
        self._win_anim_pct: float = 0.0         # 0→1 for win-line draw

        # Win line animation timer
        self._win_timer = QTimer(self)
        self._win_timer.setInterval(16)
        self._win_timer.timeout.connect(self._advance_win_anim)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(240, 240)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    # ── Public API ────────────────────────────────────────────────────

    def set_dark(self, dark: bool) -> None:
        self._dark = dark
        self.update()

    def reset(self) -> None:
        self._board = [0] * 9
        self._hovered = -1
        self._human_turn = True
        self._game_over = False
        self._winner = 0
        self._win_line = None
        self._win_anim_pct = 0.0
        self._win_timer.stop()
        self.update()

    def apply_move(self, cell: int, player: int) -> None:
        """Place player (1=X, 2=O) on cell. Checks for game end."""
        if cell < 0 or cell > 8 or self._board[cell] != 0:
            return
        self._board[cell] = player
        self._human_turn = (player == 2)   # flip turn
        self._check_end()
        self.update()

    def set_human_turn(self, val: bool) -> None:
        self._human_turn = val

    def is_game_over(self) -> bool:
        return self._game_over

    def winner(self) -> int:
        return self._winner

    def board(self) -> List[int]:
        return self._board[:]

    # ── Internal ──────────────────────────────────────────────────────

    def _check_end(self) -> None:
        w = _check_winner(self._board)
        if w:
            self._winner = w
            self._game_over = True
            # Find which line
            for a, b, c in WINNING_LINES:
                if self._board[a] == w and self._board[b] == w and self._board[c] == w:
                    self._win_line = (a, b, c)
                    break
            self._win_anim_pct = 0.0
            self._win_timer.start()
        elif all(c != 0 for c in self._board):
            self._winner = 0
            self._game_over = True

    def _advance_win_anim(self) -> None:
        self._win_anim_pct = min(1.0, self._win_anim_pct + 0.06)
        self.update()
        if self._win_anim_pct >= 1.0:
            self._win_timer.stop()

    # ── Geometry ──────────────────────────────────────────────────────

    def _cell_size(self) -> int:
        usable = min(self.width(), self.height()) - 2 * PAD - 2 * GAP
        return max(40, usable // 3)

    def _cell_rect(self, idx: int) -> QRectF:
        sz = self._cell_size()
        row, col = divmod(idx, 3)
        x = PAD + col * (sz + GAP)
        y = PAD + row * (sz + GAP)
        return QRectF(x, y, sz, sz)

    def _cell_at(self, x: float, y: float) -> int:
        for i in range(9):
            if self._cell_rect(i).contains(x, y):
                return i
        return -1

    # ── Events ────────────────────────────────────────────────────────

    def mouseMoveEvent(self, ev) -> None:  # type: ignore[override]
        idx = self._cell_at(ev.position().x(), ev.position().y())
        if idx != self._hovered:
            self._hovered = idx
            self.update()

    def leaveEvent(self, ev) -> None:  # type: ignore[override]
        self._hovered = -1
        self.update()

    def mousePressEvent(self, ev) -> None:  # type: ignore[override]
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        if self._game_over or not self._human_turn:
            return
        idx = self._cell_at(ev.position().x(), ev.position().y())
        if idx >= 0 and self._board[idx] == 0:
            self.cell_clicked.emit(idx)

    def resizeEvent(self, ev) -> None:  # type: ignore[override]
        super().resizeEvent(ev)
        self.update()

    # ── Painting ──────────────────────────────────────────────────────

    def paintEvent(self, _ev) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = DARK if self._dark else LIGHT
        sz = self._cell_size()

        # Board background
        board_w = 3 * sz + 2 * GAP
        bg_rect = QRectF(PAD - 8, PAD - 8, board_w + 16, board_w + 16)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(bg_rect, 18, 18)
        p.setBrush(QBrush(pal["panel"]))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(bg_path)

        # Win/draw background wash
        if self._game_over:
            wash = pal["win_bg"] if self._winner else pal["draw_bg"]
            p.setBrush(QBrush(wash))
            p.drawPath(bg_path)

        # Cells
        for idx in range(9):
            self._draw_cell(p, idx, pal, sz)

        # Win line
        if self._win_line and self._win_anim_pct > 0:
            self._draw_win_line(p, pal, sz)

        p.end()

    def _draw_cell(self, p: QPainter, idx: int, pal: dict, sz: int) -> None:
        rect = self._cell_rect(idx)
        val  = self._board[idx]
        is_hovered = (
            idx == self._hovered
            and not self._game_over
            and self._human_turn
            and val == 0
        )

        # Cell background
        path = QPainterPath()
        path.addRoundedRect(rect, CORNER, CORNER)

        bg = pal["cell_hover"] if is_hovered else pal["cell_bg"]
        p.setBrush(QBrush(bg))
        pen = QPen(pal["grid"], 1.5)
        p.setPen(pen)
        p.drawPath(path)

        if val == 1:
            self._draw_x(p, rect, pal, sz)
        elif val == 2:
            self._draw_o(p, rect, pal, sz)

    def _draw_x(self, p: QPainter, rect: QRectF, pal: dict, sz: int) -> None:
        m = sz * 0.22
        r = rect.adjusted(m, m, -m, -m)
        stroke = max(4, sz // 10)

        # Shadow
        shadow_pen = QPen(pal["x_shadow"], stroke + 3)
        shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(shadow_pen)
        p.drawLine(
            QPointF(r.left() + 1, r.top() + 2),
            QPointF(r.right() + 1, r.bottom() + 2)
        )
        p.drawLine(
            QPointF(r.right() + 1, r.top() + 2),
            QPointF(r.left() + 1, r.bottom() + 2)
        )
        # Main
        pen = QPen(pal["x_color"], stroke)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(r.left(), r.top()), QPointF(r.right(), r.bottom()))
        p.drawLine(QPointF(r.right(), r.top()), QPointF(r.left(), r.bottom()))

    def _draw_o(self, p: QPainter, rect: QRectF, pal: dict, sz: int) -> None:
        m = sz * 0.18
        r = rect.adjusted(m, m, -m, -m)
        stroke = max(4, sz // 10)

        # Shadow
        shadow_pen = QPen(pal["o_shadow"], stroke + 3)
        p.setPen(shadow_pen)
        p.drawEllipse(r.adjusted(1, 2, 1, 2))
        # Main
        pen = QPen(pal["o_color"], stroke)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(r)

    def _draw_win_line(self, p: QPainter, pal: dict, sz: int) -> None:
        a, b, c = self._win_line  # type: ignore[misc]
        ra = self._cell_rect(a)
        rc = self._cell_rect(c)
        start = QPointF(ra.center())
        end_full = QPointF(rc.center())

        # Interpolate endpoint by animation progress
        t = self._win_anim_pct
        end = QPointF(
            start.x() + (end_full.x() - start.x()) * t,
            start.y() + (end_full.y() - start.y()) * t,
        )

        pen = QPen(pal["win_line"], max(5, sz // 8))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(start, end)
