from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from algorithms.base import SolveResult


class StatsPanel(QWidget):
    """
    Displays algorithm statistics after a solve completes.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("stats_panel")
        self._build_ui()
        self.clear()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header
        header = QLabel("📊  Statistics")
        header.setObjectName("section_title")
        layout.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("separator")
        layout.addWidget(sep)

        # Grid of label : value pairs
        grid = QGridLayout()
        grid.setSpacing(4)
        grid.setColumnMinimumWidth(0, 120)
        grid.setColumnStretch(1, 1)

        rows = [
            ("algorithm",  "Algorithm"),
            ("time",       "Time"),
            ("expanded",   "Expanded Nodes"),
            ("generated",  "Generated Nodes"),
            ("depth",      "Depth"),
            ("moves",      "Solution Length"),
            ("memory",     "Memory Used"),
        ]

        self._fields: dict = {}
        for row_idx, (key, label) in enumerate(rows):
            lbl = QLabel(f"{label}:")
            lbl.setObjectName("stat_label")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            val = QLabel("—")
            val.setObjectName("stat_value")
            val.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            val.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )

            grid.addWidget(lbl, row_idx, 0)
            grid.addWidget(val, row_idx, 1)
            self._fields[key] = val

        layout.addLayout(grid)

    def update_stats(self, algorithm_name: str, result: SolveResult) -> None:
        """Populate all stats from a SolveResult."""
        self._fields["algorithm"].setText(algorithm_name)
        self._fields["time"].setText(f"{result.execution_time * 1000:.1f} ms")
        self._fields["expanded"].setText(f"{result.expanded_nodes:,}")
        self._fields["generated"].setText(f"{result.generated_nodes:,}")
        self._fields["depth"].setText(str(result.depth))
        self._fields["moves"].setText(str(len(result.path)))
        self._fields["memory"].setText(f"{result.memory_mb:.2f} MB")

    def clear(self) -> None:
        """Reset all stats."""
        for widget in self._fields.values():
            widget.setText("—")
