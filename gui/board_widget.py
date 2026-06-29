from __future__ import annotations
from typing import Tuple, Optional

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QTimeLine, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QPainterPath,
    QLinearGradient, QBrush
)


class BoardWidget(QWidget):
    """
    Renders the 3×3 puzzle board.
    Supports smooth CSS-style tile sliding via QTimeLine.
    """

    animation_finished = pyqtSignal()

    # Layout constants
    PADDING = 14          # px around the board
    GAP = 6               # gap between tiles
    CORNER = 10           # tile corner radius
    BOARD_RADIUS = 14     # board background corner radius

    # Colours  (light mode)
    TILE_GRAD_TOP   = QColor("#5DA0E8")
    TILE_GRAD_BOT   = QColor("#3A82C8")
    TILE_SHADOW     = QColor(0, 0, 0, 30)
    BLANK_COLOR     = QColor("#C8D4E4")
    BOARD_BG_LIGHT  = QColor("#DDE6F0")
    BOARD_BG_DARK   = QColor("#1C2A3C")
    TILE_DARK_TOP   = QColor("#4A88D4")
    TILE_DARK_BOT   = QColor("#2D6AAE")
    BLANK_DARK      = QColor("#283A50")

    def __init__(self, parent=None, dark_mode: bool = False) -> None:
        super().__init__(parent)
        self._board: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self._dark = dark_mode

        # Animation state
        self._animating = False
        self._anim_from: Tuple[int, ...] = self._board
        self._anim_to:   Tuple[int, ...] = self._board
        self._anim_tile: int = 0          # value of moving tile
        self._anim_src_idx: int = 0       # index in from_board
        self._anim_dst_idx: int = 0       # index in to_board  (= old blank)
        self._anim_t: float = 1.0         # 0.0 → 1.0  (smoothstep)
        self._timeline: Optional[QTimeLine] = None
        self._on_done_cb: Optional[callable] = None

        self.setMinimumSize(240, 240)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def set_board(self, board: Tuple[int, ...]) -> None:
        """Instantly show a board state (no animation)."""
        if self._timeline and self._timeline.state() == QTimeLine.State.Running:
            self._timeline.stop()
        self._board = board
        self._animating = False
        self._anim_t = 1.0
        self.update()

    def animate_move(
        self,
        from_board: Tuple[int, ...],
        to_board: Tuple[int, ...],
        duration_ms: int = 350,
        on_finished: Optional[callable] = None,
    ) -> None:
        """
        Slide the tile that moved between from_board and to_board.

        The blank moves from old_blank → new_blank,
        so the *tile* moves from new_blank → old_blank.
        """
        old_blank = from_board.index(0)   # blank position before
        new_blank = to_board.index(0)     # blank position after

        self._anim_from    = from_board
        self._anim_to      = to_board
        self._anim_tile    = from_board[new_blank]   # tile that fills the blank
        self._anim_src_idx = new_blank               # tile starts here
        self._anim_dst_idx = old_blank               # tile ends here
        self._anim_t       = 0.0
        self._animating    = True
        self._on_done_cb   = on_finished

        if self._timeline:
            self._timeline.stop()
            self._timeline.deleteLater()

        self._timeline = QTimeLine(duration_ms, self)
        self._timeline.setUpdateInterval(15)          # ~60 fps
        self._timeline.valueChanged.connect(self._tick)
        self._timeline.finished.connect(self._finish)
        self._timeline.start()

    def set_dark_mode(self, dark: bool) -> None:
        self._dark = dark
        self.update()

    # ------------------------------------------------------------------ #
    #  Animation internals                                                 #
    # ------------------------------------------------------------------ #

    def _tick(self, value: float) -> None:
        # smoothstep  s(t) = 3t²−2t³
        t = value
        self._anim_t = t * t * (3.0 - 2.0 * t)
        self.update()

    def _finish(self) -> None:
        self._board = self._anim_to
        self._animating = False
        self._anim_t = 1.0
        self._timeline = None
        self.update()
        self.animation_finished.emit()
        if self._on_done_cb:
            self._on_done_cb()

    # ------------------------------------------------------------------ #
    #  Geometry helpers                                                    #
    # ------------------------------------------------------------------ #

    def _tile_size(self) -> int:
        usable_w = self.width()  - 2 * self.PADDING - 2 * self.GAP
        usable_h = self.height() - 2 * self.PADDING - 2 * self.GAP
        return max(40, min(usable_w, usable_h) // 3)

    def _tile_rect(self, idx: int, sz: int) -> QRect:
        row, col = divmod(idx, 3)
        x = self.PADDING + col * (sz + self.GAP)
        y = self.PADDING + row * (sz + self.GAP)
        return QRect(x, y, sz, sz)

    # ------------------------------------------------------------------ #
    #  Painting                                                            #
    # ------------------------------------------------------------------ #

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        sz = self._tile_size()

        # ---- board background ----
        board_w = 3 * sz + 2 * self.GAP + 2 * self.PADDING - (self.PADDING - 8)
        board_h = board_w
        bg_rect_x = self.PADDING - 8
        bg_rect_y = self.PADDING - 8
        bg_rect_w = 3 * (sz + self.GAP) - self.GAP + 16
        bg_rect_h = bg_rect_w

        board_path = QPainterPath()
        board_path.addRoundedRect(
            bg_rect_x, bg_rect_y, bg_rect_w, bg_rect_h,
            self.BOARD_RADIUS, self.BOARD_RADIUS
        )
        p.setBrush(self.BOARD_BG_DARK if self._dark else self.BOARD_BG_LIGHT)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(board_path)

        # Decide which tiles to draw statically and which to animate
        moving_val = self._anim_tile if self._animating else -1

        # ---- static tiles ----
        board = self._anim_from if self._animating else self._board
        for idx, val in enumerate(board):
            if self._animating and val == moving_val and idx == self._anim_src_idx:
                continue   # will be drawn as interpolated tile
            rect = self._tile_rect(idx, sz)
            self._draw_tile(p, rect, val, sz)

        # ---- animated tile (interpolated position) ----
        if self._animating:
            src_rect = self._tile_rect(self._anim_src_idx, sz)
            dst_rect = self._tile_rect(self._anim_dst_idx, sz)
            t = self._anim_t
            ix = src_rect.x() + (dst_rect.x() - src_rect.x()) * t
            iy = src_rect.y() + (dst_rect.y() - src_rect.y()) * t
            anim_rect = QRect(int(ix), int(iy), sz, sz)
            self._draw_tile(p, anim_rect, moving_val, sz)

        p.end()

    def _draw_tile(self, p: QPainter, rect: QRect, val: int, sz: int) -> None:
        """Draw one tile (blank if val == 0)."""

        # --- shadow ---
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(
            rect.x() + 2, rect.y() + 3, rect.width(), rect.height(),
            self.CORNER, self.CORNER
        )
        p.setBrush(QBrush(self.TILE_SHADOW))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(shadow_path)

        # --- face ---
        face_path = QPainterPath()
        face_path.addRoundedRect(
            rect.x(), rect.y(), rect.width(), rect.height(),
            self.CORNER, self.CORNER
        )

        if val == 0:
            # blank tile
            p.setBrush(QBrush(self.BLANK_DARK if self._dark else self.BLANK_COLOR))
        else:
            # gradient tile
            grad = QLinearGradient(rect.x(), rect.y(), rect.x(), rect.bottom())
            if self._dark:
                grad.setColorAt(0.0, self.TILE_DARK_TOP)
                grad.setColorAt(1.0, self.TILE_DARK_BOT)
            else:
                grad.setColorAt(0.0, self.TILE_GRAD_TOP)
                grad.setColorAt(1.0, self.TILE_GRAD_BOT)
            p.setBrush(QBrush(grad))

        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(face_path)

        # --- number ---
        if val != 0:
            font_size = max(14, sz // 3)
            font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
            p.setFont(font)
            p.setPen(QPen(QColor("#FFFFFF")))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(val))

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self.update()
