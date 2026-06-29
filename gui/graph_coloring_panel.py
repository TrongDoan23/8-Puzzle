from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QSizePolicy, QSlider,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from algorithms.graph_coloring import COLOR_PALETTE, COLOR_NAMES, NUM_COLORS


class GraphColoringPanel(QWidget):

    solve_clicked       = pyqtSignal()
    reset_clicked       = pyqtSignal()
    random_graph_clicked = pyqtSignal()
    color_chosen        = pyqtSignal(int)   # user clicked swatch → color index
    speed_changed       = pyqtSignal(float)

    SPEED_VALUES = [0.25, 0.5, 1.0, 2.0, 5.0]
    SPEED_LABELS = ["0.25x", "0.5x", "1x", "2x", "5x"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._selected_color: int = -1
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ── Algorithm info ────────────────────────────────────────────
        info_group = QGroupBox("CSP — Graph Coloring")
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(10, 12, 10, 10)
        info_layout.setSpacing(4)

        self._algo_label = QLabel("Backtracking")
        self._algo_label.setObjectName("section_title")
        self._algo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._algo_desc = QLabel("")
        self._algo_desc.setObjectName("subtitle")
        self._algo_desc.setWordWrap(True)
        self._algo_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout.addWidget(self._algo_label)
        info_layout.addWidget(self._algo_desc)
        layout.addWidget(info_group)

        # ── Manual coloring — color swatches ─────────────────────────
        color_group = QGroupBox("Paint Node (click node then color)")
        color_layout = QVBoxLayout(color_group)
        color_layout.setContentsMargins(10, 10, 10, 10)
        color_layout.setSpacing(6)

        self._color_hint = QLabel("← Click a node on the graph first")
        self._color_hint.setObjectName("subtitle")
        self._color_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._color_hint.setWordWrap(True)
        color_layout.addWidget(self._color_hint)

        swatch_row = QHBoxLayout()
        swatch_row.setSpacing(6)
        self._swatch_btns: list = []
        for i in range(NUM_COLORS):
            btn = QPushButton(COLOR_NAMES[i])
            btn.setMinimumHeight(32)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_PALETTE[i]};
                    color: white;
                    border-radius: 6px;
                    font-weight: 700;
                    font-size: 11px;
                    border: 2px solid transparent;
                }}
                QPushButton:hover {{
                    border: 2px solid white;
                }}
                QPushButton:disabled {{
                    opacity: 0.4;
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self._on_color(idx))
            btn.setEnabled(False)   # enabled only when a node is selected
            self._swatch_btns.append(btn)
            swatch_row.addWidget(btn)

        color_layout.addLayout(swatch_row)
        layout.addWidget(color_group)

        # ── Controls ──────────────────────────────────────────────────
        btn_group = QGroupBox("Controls")
        btn_layout = QVBoxLayout(btn_group)
        btn_layout.setContentsMargins(10, 12, 10, 10)
        btn_layout.setSpacing(8)

        row1 = QHBoxLayout(); row1.setSpacing(8)
        self.btn_random_graph = QPushButton("🎲 Random Graph")
        self.btn_random_graph.setObjectName("btn_random")
        self.btn_random_graph.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_random_graph.setMinimumHeight(34)

        self.btn_reset = QPushButton("↩ Reset")
        self.btn_reset.setObjectName("btn_reset")
        self.btn_reset.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_reset.setMinimumHeight(34)
        row1.addWidget(self.btn_random_graph)
        row1.addWidget(self.btn_reset)

        row2 = QHBoxLayout(); row2.setSpacing(8)
        self.btn_solve = QPushButton("▶ Auto Solve")
        self.btn_solve.setObjectName("btn_solve")
        self.btn_solve.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_solve.setMinimumHeight(36)
        row2.addWidget(self.btn_solve)

        btn_layout.addLayout(row1)
        btn_layout.addLayout(row2)
        layout.addWidget(btn_group)

        # ── Speed slider ──────────────────────────────────────────────
        speed_group = QGroupBox("Animation Speed")
        speed_layout = QVBoxLayout(speed_group)
        speed_layout.setContentsMargins(10, 12, 10, 10)
        speed_layout.setSpacing(6)

        self._speed_label = QLabel("Speed: 1x")
        self._speed_label.setObjectName("stat_value")
        self._speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setMinimum(0)
        self._speed_slider.setMaximum(len(self.SPEED_VALUES) - 1)
        self._speed_slider.setValue(2)
        self._speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._speed_slider.setTickInterval(1)

        lbl_row = QHBoxLayout(); lbl_row.setContentsMargins(0, 0, 0, 0)
        for lbl in self.SPEED_LABELS:
            l = QLabel(lbl); l.setObjectName("subtitle")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_row.addWidget(l)

        speed_layout.addWidget(self._speed_label)
        speed_layout.addWidget(self._speed_slider)
        speed_layout.addLayout(lbl_row)
        layout.addWidget(speed_group)

        # ── Status ────────────────────────────────────────────────────
        self._status_label = QLabel("Click a node to color manually\nor press Auto Solve")
        self._status_label.setObjectName("subtitle")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        layout.addStretch(1)

        # Wire signals
        self.btn_solve.clicked.connect(self.solve_clicked)
        self.btn_reset.clicked.connect(self.reset_clicked)
        self.btn_random_graph.clicked.connect(self.random_graph_clicked)
        self._speed_slider.valueChanged.connect(self._on_speed)

    # ── Public API ────────────────────────────────────────────────────

    def set_algorithm(self, name: str) -> None:
        self._algo_label.setText(name)
        descs = {
            "Backtracking":     "Assigns colors one by one.\nBacktracks on conflicts.",
            "Forward Checking": "Prunes neighbor domains\nafter each assignment.",
            "AC-3":             "Enforces arc consistency first,\nthen backtracks if needed.",
            "Min-Conflicts":    "Random start, then repairs\nconflicts iteratively.",
        }
        self._algo_desc.setText(descs.get(name, ""))

    def set_status(self, text: str) -> None:
        self._status_label.setText(text)

    def set_node_selected(self, node_idx: int, node_name: str) -> None:
        """Called when user clicks a node — enable color swatches."""
        for btn in self._swatch_btns:
            btn.setEnabled(True)
        self._color_hint.setText(f"Painting: {node_name}")

    def clear_selection(self) -> None:
        for btn in self._swatch_btns:
            btn.setEnabled(False)
        self._color_hint.setText("← Click a node on the graph first")

    def set_solving(self, solving: bool) -> None:
        self.btn_solve.setEnabled(not solving)
        self.btn_reset.setEnabled(not solving)
        self.btn_random_graph.setEnabled(not solving)
        if solving:
            self.clear_selection()

    def get_speed(self) -> float:
        return self.SPEED_VALUES[self._speed_slider.value()]

    # ── Private ───────────────────────────────────────────────────────

    def _on_color(self, idx: int) -> None:
        self.color_chosen.emit(idx)
        self.clear_selection()

    def _on_speed(self, idx: int) -> None:
        self._speed_label.setText(f"Speed: {self.SPEED_LABELS[idx]}")
        self.speed_changed.emit(self.SPEED_VALUES[idx])
