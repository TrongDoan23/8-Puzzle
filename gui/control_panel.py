from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSlider, QGroupBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor

# ── Algorithm list ───────────────────────────────────────────────────────

ALGORITHM_LIST = [
    ("BFS",                           "Uninformed Search"),
    ("DFS",                           "Uninformed Search"),
    ("IDS",                           "Uninformed Search"),
    ("UCS",                           "Uninformed Search"),
    ("Greedy",                        "Informed Search"),
    ("A*",                            "Informed Search"),
    ("IDA*",                          "Informed Search"),
    ("Hill Climbing",                 "Local Search"),
    ("Steepest Ascent Hill Climbing", "Local Search"),
    ("Stochastic Hill Climbing",      "Local Search"),
    ("Random Restart Hill Climbing",  "Local Search"),
    ("Local Beam Search",             "Local Search"),
    ("Simulated Annealing",           "Local Search"),
    ("Backtracking",                  "CSP / Constraint Search"),
    ("Forward Checking",              "CSP / Constraint Search"),
    ("AC-3",                          "CSP / Constraint Search"),
    ("Min-Conflicts",                 "CSP / Constraint Search"),
    ("Sensorless Search",             "Partial Observable Search"),
    ("Belief State Search",           "Partial Observable Search"),
    ("Contingency Search",            "Partial Observable Search"),
    ("AND-OR Graph Search",           "Partial Observable Search"),
    ("Minimax",                       "Adversarial Search"),
    ("Alpha Beta",                    "Adversarial Search"),
    ("Expectiminimax",                "Adversarial Search"),
]

HEURISTIC_LIST = ["Manhattan Distance", "Misplaced Tiles", "Linear Conflict"]

SPEED_VALUES = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0]
SPEED_LABELS = ["0.25x", "0.5x", "1x", "2x", "3x", "5x"]


# ── Part 1: always-visible algorithm selector ────────────────────────────

class AlgoSelectorWidget(QWidget):
    """
    Algorithm + heuristic combo boxes.
    Always visible regardless of puzzle / TTT mode.
    """

    algo_changed = pyqtSignal(str)   # emitted on every combo change

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        group = QGroupBox("Algorithm")
        g_layout = QVBoxLayout(group)
        g_layout.setContentsMargins(10, 14, 10, 10)
        g_layout.setSpacing(6)

        # ── Algorithm combo ──────────────────────────────────────────
        algo_label = QLabel("Select Algorithm:")
        algo_label.setObjectName("subtitle")

        self.algo_combo = QComboBox()
        self.algo_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.algo_combo.setMinimumHeight(32)

        last_cat = ""
        for name, cat in ALGORITHM_LIST:
            if cat != last_cat:
                self.algo_combo.addItem(f"── {cat} ──")
                idx = self.algo_combo.count() - 1
                item = self.algo_combo.model().item(idx)
                if item:
                    item.setForeground(QBrush(QColor("#8A9BB0")))
                    item.setFlags(
                        item.flags()
                        & ~Qt.ItemFlag.ItemIsSelectable
                        & ~Qt.ItemFlag.ItemIsEnabled
                    )
                    f = item.font(); f.setItalic(True); item.setFont(f)
                last_cat = cat
            self.algo_combo.addItem(name)

        self.algo_combo.setCurrentIndex(1)  # BFS
        self.algo_combo.currentTextChanged.connect(self.algo_changed)

        # ── Heuristic combo ──────────────────────────────────────────
        heuristic_label = QLabel("Heuristic (for informed algorithms):")
        heuristic_label.setObjectName("subtitle")
        heuristic_label.setWordWrap(True)

        self.heuristic_combo = QComboBox()
        self.heuristic_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.heuristic_combo.setMinimumHeight(32)
        for h in HEURISTIC_LIST:
            self.heuristic_combo.addItem(h)

        g_layout.addWidget(algo_label)
        g_layout.addWidget(self.algo_combo)
        g_layout.addWidget(heuristic_label)
        g_layout.addWidget(self.heuristic_combo)
        layout.addWidget(group)

    # ── Public helpers ───────────────────────────────────────────────

    def get_algorithm_name(self) -> str:
        return self.algo_combo.currentText()

    def get_heuristic_name(self) -> str:
        return self.heuristic_combo.currentText()

    def set_enabled(self, enabled: bool) -> None:
        """Lock combos while solving."""
        self.algo_combo.setEnabled(enabled)
        self.heuristic_combo.setEnabled(enabled)


# ── Part 2: puzzle-specific buttons + speed ──────────────────────────────

class PuzzleControlsWidget(QWidget):
    """
    Buttons (Random / Solve / Pause / Continue / Stop / Reset)
    and the animation speed slider.
    Shown only in 8-Puzzle mode.
    """

    random_clicked   = pyqtSignal()
    solve_clicked    = pyqtSignal()
    pause_clicked    = pyqtSignal()
    continue_clicked = pyqtSignal()
    stop_clicked     = pyqtSignal()
    reset_clicked    = pyqtSignal()
    speed_changed    = pyqtSignal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()
        self.set_state_idle()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ── Buttons ──────────────────────────────────────────────────
        btn_group = QGroupBox("Controls")
        btn_layout = QVBoxLayout(btn_group)
        btn_layout.setContentsMargins(10, 14, 10, 10)
        btn_layout.setSpacing(8)

        def _row(*btns):
            row = QHBoxLayout(); row.setSpacing(8)
            for b in btns: row.addWidget(b)
            return row

        self.btn_random   = self._btn("🎲 Random",   "btn_random")
        self.btn_solve    = self._btn("▶ Solve",      "btn_solve")
        self.btn_pause    = self._btn("⏸ Pause",      "btn_pause")
        self.btn_continue = self._btn("⏵ Continue",  "btn_continue")
        self.btn_stop     = self._btn("⏹ Stop",       "btn_stop")
        self.btn_reset    = self._btn("↩ Reset",      "btn_reset")

        btn_layout.addLayout(_row(self.btn_random,   self.btn_solve))
        btn_layout.addLayout(_row(self.btn_pause,    self.btn_continue))
        btn_layout.addLayout(_row(self.btn_stop,     self.btn_reset))
        layout.addWidget(btn_group)

        # ── Speed slider ─────────────────────────────────────────────
        speed_group = QGroupBox("Animation Speed")
        speed_layout = QVBoxLayout(speed_group)
        speed_layout.setContentsMargins(10, 14, 10, 10)
        speed_layout.setSpacing(6)

        self.speed_label = QLabel("Speed: 1x")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_label.setObjectName("stat_value")

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(len(SPEED_VALUES) - 1)
        self.speed_slider.setValue(2)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(1)

        lbl_row = QHBoxLayout(); lbl_row.setContentsMargins(0, 0, 0, 0)
        for lbl in SPEED_LABELS:
            l = QLabel(lbl); l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.setObjectName("subtitle"); lbl_row.addWidget(l)

        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addLayout(lbl_row)
        layout.addWidget(speed_group)

        # ── Wire signals ─────────────────────────────────────────────
        self.btn_random.clicked.connect(self.random_clicked)
        self.btn_solve.clicked.connect(self.solve_clicked)
        self.btn_pause.clicked.connect(self.pause_clicked)
        self.btn_continue.clicked.connect(self.continue_clicked)
        self.btn_stop.clicked.connect(self.stop_clicked)
        self.btn_reset.clicked.connect(self.reset_clicked)
        self.speed_slider.valueChanged.connect(self._on_speed)

    @staticmethod
    def _btn(text: str, obj_name: str) -> QPushButton:
        b = QPushButton(text); b.setObjectName(obj_name)
        b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return b

    def _on_speed(self, idx: int) -> None:
        self.speed_label.setText(f"Speed: {SPEED_LABELS[idx]}")
        self.speed_changed.emit(SPEED_VALUES[idx])

    def get_speed(self) -> float:
        return SPEED_VALUES[self.speed_slider.value()]

    # ── State management ─────────────────────────────────────────────

    def set_state_idle(self) -> None:
        self.btn_random.setEnabled(True);   self.btn_solve.setEnabled(True)
        self.btn_pause.setEnabled(False);   self.btn_continue.setEnabled(False)
        self.btn_stop.setEnabled(False);    self.btn_reset.setEnabled(True)

    def set_state_solving(self) -> None:
        self.btn_random.setEnabled(False);  self.btn_solve.setEnabled(False)
        self.btn_pause.setEnabled(True);    self.btn_continue.setEnabled(False)
        self.btn_stop.setEnabled(True);     self.btn_reset.setEnabled(False)

    def set_state_paused(self) -> None:
        self.btn_pause.setEnabled(False);   self.btn_continue.setEnabled(True)
        self.btn_stop.setEnabled(True)

    def set_state_done(self) -> None:
        self.btn_random.setEnabled(True);   self.btn_solve.setEnabled(True)
        self.btn_pause.setEnabled(False);   self.btn_continue.setEnabled(False)
        self.btn_stop.setEnabled(False);    self.btn_reset.setEnabled(True)


# ── Compatibility shim ───────────────────────────────────────────────────
# main_window.py still references ControlPanel in a few places;
# keep a thin wrapper so nothing breaks.

class ControlPanel(QWidget):
    """
    Legacy wrapper — combines AlgoSelectorWidget + PuzzleControlsWidget.
    Used only when main_window accesses self._control_panel directly.
    """

    random_clicked   = pyqtSignal()
    solve_clicked    = pyqtSignal()
    pause_clicked    = pyqtSignal()
    continue_clicked = pyqtSignal()
    stop_clicked     = pyqtSignal()
    reset_clicked    = pyqtSignal()
    speed_changed    = pyqtSignal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._algo = AlgoSelectorWidget()
        self._controls = PuzzleControlsWidget()

        layout.addWidget(self._algo)
        layout.addWidget(self._controls)

        # Forward signals
        self._controls.random_clicked.connect(self.random_clicked)
        self._controls.solve_clicked.connect(self.solve_clicked)
        self._controls.pause_clicked.connect(self.pause_clicked)
        self._controls.continue_clicked.connect(self.continue_clicked)
        self._controls.stop_clicked.connect(self.stop_clicked)
        self._controls.reset_clicked.connect(self.reset_clicked)
        self._controls.speed_changed.connect(self.speed_changed)

    # ── Delegate property access ──────────────────────────────────────

    @property
    def algo_combo(self):
        return self._algo.algo_combo

    @property
    def heuristic_combo(self):
        return self._algo.heuristic_combo

    def get_algorithm_name(self) -> str:
        return self._algo.get_algorithm_name()

    def get_heuristic_name(self) -> str:
        return self._algo.get_heuristic_name()

    def get_speed(self) -> float:
        return self._controls.get_speed()

    def set_state_idle(self) -> None:
        self._algo.set_enabled(True)
        self._controls.set_state_idle()

    def set_state_solving(self) -> None:
        self._algo.set_enabled(False)
        self._controls.set_state_solving()

    def set_state_paused(self) -> None:
        self._controls.set_state_paused()

    def set_state_done(self) -> None:
        self._algo.set_enabled(True)
        self._controls.set_state_done()
