from __future__ import annotations
from typing import List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QGroupBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal

DIRECTION_ICONS = {'U': '↑', 'D': '↓', 'L': '←', 'R': '→'}
DIRECTION_NAMES = {'U': 'Up', 'D': 'Down', 'L': 'Left', 'R': 'Right'}


class SolutionPanel(QWidget):
    """
    Scrollable list of solution steps.
    Designed to sit to the right of the board and fill all available height.
    Clicking a step emits step_clicked(index).
    """

    step_clicked = pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._moves: List[str] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        group = QGroupBox("Solution Steps")
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 10, 8, 8)
        group_layout.setSpacing(6)

        self._count_label = QLabel("No solution")
        self._count_label.setObjectName("subtitle")
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._list = QListWidget()
        # Let the list grow to fill whatever height the panel gets
        self._list.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._list.setMinimumHeight(120)
        self._list.itemClicked.connect(self._on_item_clicked)

        group_layout.addWidget(self._count_label)
        group_layout.addWidget(self._list, stretch=1)
        layout.addWidget(group, stretch=1)

    # ------------------------------------------------------------------ #

    def set_solution(self, moves: List[str]) -> None:
        self._moves = moves
        self._list.clear()

        if not moves:
            self._count_label.setText("No steps")
            return

        self._count_label.setText(f"{len(moves)} steps total")
        for i, move in enumerate(moves):
            icon = DIRECTION_ICONS.get(move, move)
            name = DIRECTION_NAMES.get(move, move)
            item = QListWidgetItem(f"  Step {i + 1:>3}   {icon}  Move {name}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self._list.addItem(item)

    def highlight_step(self, step_index: int) -> None:
        self._list.blockSignals(True)
        if 0 <= step_index < self._list.count():
            self._list.setCurrentRow(step_index)
            item = self._list.item(step_index)
            if item:
                self._list.scrollToItem(item)
        else:
            self._list.clearSelection()
        self._list.blockSignals(False)

    def clear(self) -> None:
        self._moves = []
        self._list.clear()
        self._count_label.setText("No solution")

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is not None:
            self.step_clicked.emit(int(idx))
