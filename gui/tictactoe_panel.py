from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QSizePolicy, QFrame,
    QComboBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class TicTacToePanel(QWidget):
    """
    Controls for the Tic-Tac-Toe game mode:
    - Algorithm label
    - Who goes first selector
    - New Game button
    - Score board
    - Move history
    """

    new_game_clicked  = pyqtSignal()
    first_player_changed = pyqtSignal(str)   # "human" or "ai"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()
        self.reset_score()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ── Algorithm info ──────────────────────────────────────────
        info_group = QGroupBox("Adversarial Search")
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(10, 12, 10, 10)
        info_layout.setSpacing(4)

        self._algo_label = QLabel("Minimax")
        self._algo_label.setObjectName("section_title")
        self._algo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._algo_desc = QLabel("")
        self._algo_desc.setObjectName("subtitle")
        self._algo_desc.setWordWrap(True)
        self._algo_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout.addWidget(self._algo_label)
        info_layout.addWidget(self._algo_desc)
        layout.addWidget(info_group)

        # ── Game settings ───────────────────────────────────────────
        settings_group = QGroupBox("Game Settings")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setContentsMargins(10, 12, 10, 10)
        settings_layout.setSpacing(8)

        first_label = QLabel("Who goes first?")
        first_label.setObjectName("subtitle")
        self._first_combo = QComboBox()
        self._first_combo.addItems(["Human (X)", "AI (O)"])
        self._first_combo.setMinimumHeight(32)
        self._first_combo.currentIndexChanged.connect(self._on_first_changed)

        self._btn_new = QPushButton("🎮  New Game")
        self._btn_new.setObjectName("btn_solve")
        self._btn_new.setMinimumHeight(38)
        self._btn_new.clicked.connect(self.new_game_clicked)

        settings_layout.addWidget(first_label)
        settings_layout.addWidget(self._first_combo)
        settings_layout.addWidget(self._btn_new)
        layout.addWidget(settings_group)

        # ── Score board ─────────────────────────────────────────────
        score_group = QGroupBox("Score")
        score_layout = QVBoxLayout(score_group)
        score_layout.setContentsMargins(10, 12, 10, 10)
        score_layout.setSpacing(6)

        row = QHBoxLayout()

        # Human score
        human_col = QVBoxLayout()
        lbl_you = QLabel("You (X)")
        lbl_you.setObjectName("subtitle")
        lbl_you.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._score_human = QLabel("0")
        self._score_human.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._score_human.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self._score_human.setObjectName("stat_value")
        human_col.addWidget(lbl_you)
        human_col.addWidget(self._score_human)

        # Draw score
        draw_col = QVBoxLayout()
        lbl_draw = QLabel("Draw")
        lbl_draw.setObjectName("subtitle")
        lbl_draw.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._score_draw = QLabel("0")
        self._score_draw.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._score_draw.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self._score_draw.setObjectName("stat_value")
        draw_col.addWidget(lbl_draw)
        draw_col.addWidget(self._score_draw)

        # AI score
        ai_col = QVBoxLayout()
        lbl_ai = QLabel("AI (O)")
        lbl_ai.setObjectName("subtitle")
        lbl_ai.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._score_ai = QLabel("0")
        self._score_ai.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._score_ai.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self._score_ai.setObjectName("stat_value")
        ai_col.addWidget(lbl_ai)
        ai_col.addWidget(self._score_ai)

        row.addLayout(human_col)
        row.addLayout(draw_col)
        row.addLayout(ai_col)
        score_layout.addLayout(row)

        # Reset score button
        self._btn_reset_score = QPushButton("Reset Score")
        self._btn_reset_score.setObjectName("btn_reset")
        self._btn_reset_score.setMinimumHeight(30)
        self._btn_reset_score.clicked.connect(self.reset_score)
        score_layout.addWidget(self._btn_reset_score)
        layout.addWidget(score_group)

        # ── Status ──────────────────────────────────────────────────
        self._status_label = QLabel("Press New Game to start")
        self._status_label.setObjectName("subtitle")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        layout.addStretch(1)

    # ── Public methods ───────────────────────────────────────────────

    def set_algorithm(self, name: str) -> None:
        self._algo_label.setText(name)
        descs = {
            "Minimax": "Explores full game tree.\nAI plays perfectly — unbeatable.",
            "Alpha Beta": "Minimax with pruning.\nFaster, equally unbeatable.",
            "Expectiminimax": "Adds randomness (15%).\nAI occasionally makes mistakes!",
        }
        self._algo_desc.setText(descs.get(name, ""))

    def set_status(self, text: str) -> None:
        self._status_label.setText(text)

    def add_result(self, winner: int) -> None:
        """winner: 0=draw, 1=human, 2=AI"""
        if winner == 1:
            self._wins_human += 1
        elif winner == 2:
            self._wins_ai += 1
        else:
            self._wins_draw += 1
        self._refresh_score()

    def reset_score(self) -> None:
        self._wins_human = 0
        self._wins_ai = 0
        self._wins_draw = 0
        self._refresh_score()

    def human_first(self) -> bool:
        return self._first_combo.currentIndex() == 0

    # ── Private ──────────────────────────────────────────────────────

    def _refresh_score(self) -> None:
        self._score_human.setText(str(self._wins_human))
        self._score_ai.setText(str(self._wins_ai))
        self._score_draw.setText(str(self._wins_draw))

    def _on_first_changed(self, idx: int) -> None:
        self.first_player_changed.emit("human" if idx == 0 else "ai")
