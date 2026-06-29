from __future__ import annotations
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame,
    QMessageBox, QSizePolicy, QStackedWidget,
)
from PyQt6.QtCore import Qt, QTimer, QThread, QObject, pyqtSignal

from gui.board_widget import BoardWidget
from gui.control_panel import AlgoSelectorWidget, PuzzleControlsWidget
from gui.stats_panel import StatsPanel
from gui.solution_panel import SolutionPanel
from gui.tictactoe_widget import TicTacToeWidget
from gui.tictactoe_panel import TicTacToePanel
from gui.graph_coloring_widget import GraphColoringWidget
from gui.graph_coloring_panel import GraphColoringPanel
from gui.styles import get_stylesheet, LIGHT_PALETTE, DARK_PALETTE
from models.state import GOAL_STATE
from models.puzzle import Puzzle
from utils.random_board import generate_random_board
from utils.animation import get_animation_duration
from utils.heuristic import HEURISTICS
from algorithms.base import SolveResult

from algorithms.bfs import BFS
from algorithms.dfs import DFS
from algorithms.ids import IDS
from algorithms.ucs import UCS
from algorithms.greedy import Greedy
from algorithms.astar import AStar
from algorithms.ida import IDAStar
from algorithms.hill_climbing import HillClimbing
from algorithms.steepest_ascent import SteepestAscent
from algorithms.stochastic_hc import StochasticHC
from algorithms.random_restart import RandomRestartHC
from algorithms.beam_search import BeamSearch
from algorithms.simulated_annealing import SimulatedAnnealing
from algorithms.sensorless import SensorlessSearch
from algorithms.belief_state import BeliefStateSearch
from algorithms.contingency import ContingencySearch
from algorithms.and_or import AndOrSearch
from algorithms.minimax import Minimax, AlphaBeta, Expectiminimax, _check_winner
from algorithms.graph_coloring import (
    GCBacktracking, GCForwardChecking, GCAC3, GCMinConflicts,
    generate_random_graph, AUSTRALIA, UNASSIGNED as GC_UNASSIGNED,
)

ALGORITHM_MAP = {
    "BFS": BFS, "DFS": DFS, "IDS": IDS, "UCS": UCS,
    "Greedy": Greedy, "A*": AStar, "IDA*": IDAStar,
    "Hill Climbing": HillClimbing,
    "Steepest Ascent Hill Climbing": SteepestAscent,
    "Stochastic Hill Climbing": StochasticHC,
    "Random Restart Hill Climbing": RandomRestartHC,
    "Local Beam Search": BeamSearch,
    "Simulated Annealing": SimulatedAnnealing,
    "Sensorless Search": SensorlessSearch,
    "Belief State Search": BeliefStateSearch,
    "Contingency Search": ContingencySearch,
    "AND-OR Graph Search": AndOrSearch,
    "Minimax": Minimax, "Alpha Beta": AlphaBeta,
    "Expectiminimax": Expectiminimax,
}

# GC algorithms — handled separately (don't solve 8-puzzle)
GC_ALGORITHM_MAP = {
    "Backtracking":     GCBacktracking,
    "Forward Checking": GCForwardChecking,
    "AC-3":             GCAC3,
    "Min-Conflicts":    GCMinConflicts,
}

TTT_ALGORITHMS = {"Minimax", "Alpha Beta", "Expectiminimax"}
GC_ALGORITHMS  = {"Backtracking", "Forward Checking", "AC-3", "Min-Conflicts"}


# ── Solver worker (8-puzzle only) ────────────────────────────────────────

class SolverWorker(QObject):
    finished = pyqtSignal(object)

    def __init__(self, algo_name: str, board: tuple, heuristic_name: str) -> None:
        super().__init__()
        self._algo_name = algo_name
        self._board = board
        self._heuristic_name = heuristic_name
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        if self._cancelled:
            return
        algo_class = ALGORITHM_MAP.get(self._algo_name)
        if algo_class is None:
            if not self._cancelled:
                self.finished.emit(SolveResult.failure("Algorithm not found."))
            return
        algo = algo_class()
        h_fn = HEURISTICS.get(self._heuristic_name)
        try:
            result = algo.solve(self._board, GOAL_STATE, h_fn)
        except Exception as exc:
            result = SolveResult.failure(f"Unexpected error: {exc}")
        if not self._cancelled:
            self.finished.emit(result)


# ── Main Window ──────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """Main application window — hosts both 8-Puzzle and Tic-Tac-Toe modes."""

    def __init__(self) -> None:
        super().__init__()
        self._dark_mode = False
        self._puzzle = Puzzle()
        self._solution_states: List[Tuple[int, ...]] = []
        self._solution_moves: List[str] = []
        self._current_step: int = 0
        self._is_paused: bool = False
        self._is_animating: bool = False
        self._is_solving: bool = False
        self._speed: float = 1.0
        self._solve_thread: Optional[QThread] = None
        self._worker: Optional[SolverWorker] = None

        # TTT state
        self._ttt_algo: Optional[object] = None
        self._ttt_mode: bool = False

        # Graph Coloring state
        self._gc_algo: Optional[object] = None
        self._gc_mode: bool = False
        self._gc_steps: list = []
        self._gc_step_idx: int = 0
        self._gc_timer = QTimer()
        self._gc_timer.timeout.connect(self._gc_advance_step)
        self._gc_speed: float = 1.0
        self._gc_current_graph = AUSTRALIA

        self._build_ui()
        self._apply_theme()
        self._update_board_display(GOAL_STATE)

        # Watch algorithm selection — drives mode switching
        self._algo_selector.algo_changed.connect(self._on_algo_changed)

    # ── UI construction ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("8-Puzzle Solver")
        self.setMinimumSize(960, 620)
        self.resize(1160, 720)

        central = QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ── CENTER PANEL (stacked: puzzle view / ttt view) ───────────
        center = QWidget()
        center.setObjectName("left_panel")
        center.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(16, 16, 16, 16)
        center_layout.setSpacing(10)

        self._center_title = QLabel("8-Puzzle Board")
        self._center_title.setObjectName("section_title")
        self._center_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self._center_title)

        # Stacked widget: index 0 = puzzle, index 1 = ttt
        self._center_stack = QStackedWidget()
        center_layout.addWidget(self._center_stack, stretch=1)

        # Page 0 — 8-Puzzle board + solution side-by-side
        puzzle_page = QWidget()
        puzzle_layout = QHBoxLayout(puzzle_page)
        puzzle_layout.setContentsMargins(0, 0, 0, 0)
        puzzle_layout.setSpacing(12)

        self._board_widget = BoardWidget(dark_mode=self._dark_mode)
        self._board_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._board_widget.setMinimumSize(240, 240)
        self._board_widget.animation_finished.connect(self._on_animation_finished)
        puzzle_layout.addWidget(self._board_widget, stretch=5)

        self._solution_panel = SolutionPanel()
        self._solution_panel.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        self._solution_panel.setMinimumWidth(200)
        puzzle_layout.addWidget(self._solution_panel, stretch=3)

        self._center_stack.addWidget(puzzle_page)

        # Page 1 — Tic-Tac-Toe board
        ttt_page = QWidget()
        ttt_layout = QHBoxLayout(ttt_page)
        ttt_layout.setContentsMargins(0, 0, 0, 0)
        ttt_layout.setSpacing(0)

        self._ttt_widget = TicTacToeWidget(dark=self._dark_mode)
        self._ttt_widget.cell_clicked.connect(self._on_ttt_cell_clicked)
        ttt_layout.addWidget(self._ttt_widget)

        self._center_stack.addWidget(ttt_page)

        # Page 2 — Graph Coloring board
        gc_page = QWidget()
        gc_layout = QHBoxLayout(gc_page)
        gc_layout.setContentsMargins(0, 0, 0, 0)
        self._gc_widget = GraphColoringWidget(dark=self._dark_mode)
        gc_layout.addWidget(self._gc_widget)
        self._center_stack.addWidget(gc_page)

        self._center_stack.setCurrentIndex(0)

        # Status + separator + stats (shared)
        self._status_label = QLabel("Ready")
        self._status_label.setObjectName("subtitle")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setWordWrap(True)
        center_layout.addWidget(self._status_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("separator")
        center_layout.addWidget(sep)

        self._stats_panel = StatsPanel()
        center_layout.addWidget(self._stats_panel, stretch=0)

        root.addWidget(center, stretch=1)

        # ── RIGHT PANEL ──────────────────────────────────────────────
        right_scroll = QScrollArea()
        right_scroll.setObjectName("right_scroll")
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_scroll.setFixedWidth(300)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)

        right_inner = QWidget()
        right_inner.setObjectName("right_panel")
        right_layout = QVBoxLayout(right_inner)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(12)

        # Title + dark-mode toggle — always visible
        top_row = QHBoxLayout()
        right_title = QLabel("Controls")
        right_title.setObjectName("section_title")
        self._dark_mode_btn = _ThemeToggleButton(dark=self._dark_mode)
        self._dark_mode_btn.clicked.connect(self._toggle_dark_mode)
        top_row.addWidget(right_title)
        top_row.addStretch()
        top_row.addWidget(self._dark_mode_btn)
        right_layout.addLayout(top_row)

        # ── Algorithm selector — ALWAYS VISIBLE ──────────────────────
        self._algo_selector = AlgoSelectorWidget()
        right_layout.addWidget(self._algo_selector)

        # Thin separator
        sep_r = QFrame()
        sep_r.setFrameShape(QFrame.Shape.HLine)
        sep_r.setObjectName("separator")
        right_layout.addWidget(sep_r)

        # ── Mode-specific controls (swapped by QStackedWidget) ────────
        self._mode_stack = QStackedWidget()

        # Index 0 — puzzle buttons + speed slider
        self._puzzle_controls = PuzzleControlsWidget()
        self._mode_stack.addWidget(self._puzzle_controls)

        # Index 1 — TTT game panel
        self._ttt_panel = TicTacToePanel()
        self._mode_stack.addWidget(self._ttt_panel)

        # Index 2 — Graph Coloring panel
        self._gc_panel = GraphColoringPanel()
        self._mode_stack.addWidget(self._gc_panel)

        self._mode_stack.setCurrentIndex(0)
        right_layout.addWidget(self._mode_stack)
        right_layout.addStretch(1)

        right_scroll.setWidget(right_inner)
        root.addWidget(right_scroll, stretch=0)

        self.statusBar().showMessage("Welcome to 8-Puzzle Solver!")

        # ── Connect puzzle control signals ────────────────────────────
        self._puzzle_controls.random_clicked.connect(self._on_random)
        self._puzzle_controls.solve_clicked.connect(self._on_solve)
        self._puzzle_controls.pause_clicked.connect(self._on_pause)
        self._puzzle_controls.continue_clicked.connect(self._on_continue)
        self._puzzle_controls.stop_clicked.connect(self._on_stop)
        self._puzzle_controls.reset_clicked.connect(self._on_reset)
        self._puzzle_controls.speed_changed.connect(self._on_speed_changed)
        self._solution_panel.step_clicked.connect(self._on_step_clicked)

        # ── Connect TTT signals ───────────────────────────────────────
        self._ttt_panel.new_game_clicked.connect(self._ttt_new_game)
        self._ttt_panel.first_player_changed.connect(self._ttt_first_changed)

        # ── Connect GC signals ────────────────────────────────────────
        self._gc_panel.solve_clicked.connect(self._gc_solve)
        self._gc_panel.reset_clicked.connect(self._gc_reset)
        self._gc_panel.random_graph_clicked.connect(self._gc_random_graph)
        self._gc_panel.color_chosen.connect(self._gc_color_chosen)
        self._gc_panel.speed_changed.connect(self._gc_speed_changed)
        self._gc_widget.node_clicked.connect(self._gc_node_clicked)

    # ── Theme ────────────────────────────────────────────────────────

    def _apply_theme(self) -> None:
        palette = DARK_PALETTE if self._dark_mode else LIGHT_PALETTE
        self.setStyleSheet(get_stylesheet(palette))
        self._board_widget.set_dark_mode(self._dark_mode)
        self._ttt_widget.set_dark(self._dark_mode)
        self._gc_widget.set_dark(self._dark_mode)
        self._dark_mode_btn.set_dark(self._dark_mode)

    def _toggle_dark_mode(self) -> None:
        self._dark_mode = not self._dark_mode
        self._apply_theme()

    # ── Mode switching ───────────────────────────────────────────────

    def _on_algo_changed(self, algo_name: str) -> None:
        """Switch between puzzle / TTT / Graph Coloring mode."""
        if algo_name in TTT_ALGORITHMS:
            self._exit_gc_mode()
            self._enter_ttt_mode(algo_name)
        elif algo_name in GC_ALGORITHMS:
            self._exit_ttt_mode()
            self._enter_gc_mode(algo_name)
        else:
            self._exit_ttt_mode()
            self._exit_gc_mode()
            self._enter_puzzle_mode()

    def _enter_ttt_mode(self, algo_name: str) -> None:
        self._ttt_panel.set_algorithm(algo_name)
        self._ttt_algo = ALGORITHM_MAP[algo_name]()
        if self._ttt_mode:
            return
        self._stop_solver()
        self._ttt_mode = True
        self._center_stack.setCurrentIndex(1)
        self._mode_stack.setCurrentIndex(1)
        self._center_title.setText("Tic-Tac-Toe  ✕  ○")
        self._ttt_widget.reset()
        self._stats_panel.clear()
        self._status_label.setText("Press New Game to start!")
        self.statusBar().showMessage(f"Tic-Tac-Toe mode — AI uses {algo_name}")

    def _exit_ttt_mode(self) -> None:
        if not self._ttt_mode:
            return
        self._ttt_mode = False
        self._ttt_algo = None

    def _enter_puzzle_mode(self) -> None:
        self._center_stack.setCurrentIndex(0)
        self._mode_stack.setCurrentIndex(0)
        self._center_title.setText("8-Puzzle Board")
        self._status_label.setText("Ready")
        self.statusBar().showMessage("8-Puzzle mode")

    def _enter_gc_mode(self, algo_name: str) -> None:
        self._gc_panel.set_algorithm(algo_name)
        self._gc_algo = GC_ALGORITHM_MAP[algo_name]()
        if self._gc_mode:
            return
        self._stop_solver()
        self._gc_mode = True
        self._center_stack.setCurrentIndex(2)
        self._mode_stack.setCurrentIndex(2)
        self._center_title.setText("Graph Coloring — CSP Demo")
        self._gc_widget.set_graph(self._gc_current_graph)
        self._stats_panel.clear()
        self._status_label.setText(
            "Click a node to color manually, or press Auto Solve."
        )
        self.statusBar().showMessage(f"Graph Coloring mode — {algo_name}")

    def _exit_gc_mode(self) -> None:
        if not self._gc_mode:
            return
        self._gc_timer.stop()
        self._gc_mode = False
        self._gc_algo = None
        self._gc_steps = []
        self._gc_step_idx = 0
        self._gc_current_graph = AUSTRALIA

    # ── Board display ────────────────────────────────────────────────

    def _update_board_display(self, board: Tuple[int, ...]) -> None:
        self._board_widget.set_board(board)

    # ── Thread management ────────────────────────────────────────────

    def _stop_solver(self) -> None:
        if self._worker is not None:
            self._worker.cancel()
            try:
                self._worker.finished.disconnect()
            except TypeError:
                pass
        if self._solve_thread is not None:
            if self._solve_thread.isRunning():
                self._solve_thread.quit()
                if not self._solve_thread.wait(500):
                    self._solve_thread.terminate()
                    self._solve_thread.wait(200)
        self._worker = None
        self._solve_thread = None
        self._is_solving = False

    # ── 8-Puzzle button handlers ─────────────────────────────────────

    def _on_random(self) -> None:
        self._stop_solver()
        self._is_paused = True
        self._is_animating = False
        board = generate_random_board(num_moves=60)
        self._puzzle.set_board(board)
        self._solution_moves = []
        self._solution_states = []
        self._current_step = 0
        self._solution_panel.clear()
        self._stats_panel.clear()
        self._update_board_display(board)
        self._puzzle_controls.set_state_idle()
        self._algo_selector.set_enabled(True)
        self._status_label.setText("Board randomized — press Solve to run an algorithm.")
        self.statusBar().showMessage("Random board generated.")

    def _on_solve(self) -> None:
        if self._is_solving:
            return
        algo_name = self._algo_selector.get_algorithm_name()
        if algo_name.startswith("──"):
            self._status_label.setText("Please select a valid algorithm.")
            return
        board = self._puzzle.board
        if board == GOAL_STATE:
            self._status_label.setText("Already at goal state!")
            return
        heuristic_name = self._algo_selector.get_heuristic_name()
        self._is_paused = False
        self._is_animating = False
        self._solution_moves = []
        self._solution_states = []
        self._current_step = 0
        self._solution_panel.clear()
        self._stats_panel.clear()
        self._status_label.setText(f"Running {algo_name}…")
        self._puzzle_controls.set_state_solving()
        self._algo_selector.set_enabled(False)
        self.statusBar().showMessage(f"Solving with {algo_name}…")
        self._is_solving = True
        self._worker = SolverWorker(algo_name, board, heuristic_name)
        self._solve_thread = QThread(self)
        self._worker.moveToThread(self._solve_thread)
        self._solve_thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_solve_finished)
        self._worker.finished.connect(self._solve_thread.quit)
        self._solve_thread.start()

    def _on_solve_finished(self, result: SolveResult) -> None:
        if self._worker is None or not self._is_solving:
            return
        self._is_solving = False
        algo_name = self._algo_selector.get_algorithm_name()
        self._stats_panel.update_stats(algo_name, result)
        if not result.success:
            msg = result.message or "No solution found."
            self._show_message(msg, algo_name)
            self._puzzle_controls.set_state_done()
            self._algo_selector.set_enabled(True)
            self._status_label.setText(msg)
            self.statusBar().showMessage("Finished — no solution.")
            return
        if not result.path:
            self._puzzle_controls.set_state_done()
            self._algo_selector.set_enabled(True)
            self._status_label.setText("Already at goal state!")
            return
        self._solution_moves = result.path
        self._solution_states = self._build_state_sequence(self._puzzle.board, result.path)
        self._current_step = 0
        self._is_paused = False
        self._solution_panel.set_solution(result.path)
        self._status_label.setText(f"Found {len(result.path)}-step solution. Animating…")
        self.statusBar().showMessage(f"Solution: {len(result.path)} moves.")
        self._animate_next_step()

    def _show_message(self, message: str, title: str) -> None:
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def _build_state_sequence(self, initial: Tuple[int, ...], moves: List[str]) -> List[Tuple[int, ...]]:
        from models.state import DIRECTIONS
        states = [initial]
        current = list(initial)
        for move in moves:
            blank = current.index(0)
            new_blank = blank + DIRECTIONS[move]
            current[blank], current[new_blank] = current[new_blank], current[blank]
            states.append(tuple(current))
        return states

    def _animate_next_step(self) -> None:
        if self._is_paused or not self._solution_states:
            return
        if self._current_step >= len(self._solution_moves):
            self._on_animation_all_done()
            return
        from_board = self._solution_states[self._current_step]
        to_board   = self._solution_states[self._current_step + 1]
        self._is_animating = True
        self._solution_panel.highlight_step(self._current_step)
        self._board_widget.animate_move(from_board, to_board, get_animation_duration(self._speed))

    def _on_animation_finished(self) -> None:
        self._is_animating = False
        if not self._solution_states:
            return
        self._current_step += 1
        if self._is_paused:
            return
        if self._current_step < len(self._solution_moves):
            QTimer.singleShot(max(20, int(50 / self._speed)), self._animate_next_step)
        else:
            self._on_animation_all_done()

    def _on_animation_all_done(self) -> None:
        self._puzzle_controls.set_state_done()
        self._algo_selector.set_enabled(True)
        self._status_label.setText("✅ Solved! Puzzle complete.")
        self.statusBar().showMessage("Animation complete.")
        self._board_widget.set_board(GOAL_STATE)

    def _on_pause(self) -> None:
        self._is_paused = True
        self._puzzle_controls.set_state_paused()
        self._status_label.setText("⏸ Paused.")

    def _on_continue(self) -> None:
        if not self._solution_states:
            return
        self._is_paused = False
        self._puzzle_controls.set_state_solving()
        self._status_label.setText("Continuing animation…")
        if not self._is_animating:
            self._animate_next_step()

    def _on_stop(self) -> None:
        self._is_paused = True
        self._is_animating = False
        self._solution_moves = []
        self._solution_states = []
        self._stop_solver()
        self._puzzle_controls.set_state_idle()
        self._algo_selector.set_enabled(True)
        self._status_label.setText("Stopped.")

    def _on_reset(self) -> None:
        self._is_paused = True
        self._is_animating = False
        self._solution_moves = []
        self._solution_states = []
        self._stop_solver()
        self._current_step = 0
        self._solution_panel.clear()
        self._stats_panel.clear()
        self._puzzle.reset()
        self._update_board_display(self._puzzle.board)
        self._puzzle_controls.set_state_idle()
        self._algo_selector.set_enabled(True)
        self._status_label.setText("Board reset to initial state.")

    def _on_speed_changed(self, speed: float) -> None:
        self._speed = speed

    def _on_step_clicked(self, step_index: int) -> None:
        if not self._solution_states:
            return
        target = step_index + 1
        if 0 <= target < len(self._solution_states):
            self._update_board_display(self._solution_states[target])
            self._current_step = target
            self._solution_panel.highlight_step(step_index)

    # ── Tic-Tac-Toe handlers ─────────────────────────────────────────

    def _ttt_new_game(self) -> None:
        """Start a new Tic-Tac-Toe game."""
        self._ttt_widget.reset()
        self._stats_panel.clear()

        if self._ttt_panel.human_first():
            self._ttt_widget.set_human_turn(True)
            self._ttt_panel.set_status("Your turn — click a cell (X)")
            self._status_label.setText("Your turn — you are X")
        else:
            self._ttt_widget.set_human_turn(False)
            self._ttt_panel.set_status("AI is thinking…")
            self._status_label.setText("AI goes first…")
            QTimer.singleShot(400, self._ttt_ai_move)

    def _ttt_first_changed(self, who: str) -> None:
        """Called when human/AI first selector changes."""
        pass  # applied on next New Game

    def _on_ttt_cell_clicked(self, cell: int) -> None:
        """Human places X on the clicked cell."""
        if self._ttt_widget.is_game_over():
            return
        # Human move (player=1 → X)
        self._ttt_widget.apply_move(cell, 1)
        self.update()

        if self._ttt_widget.is_game_over():
            self._ttt_game_ended()
            return

        # AI's turn — small delay so the human move renders first
        self._ttt_widget.set_human_turn(False)
        self._ttt_panel.set_status("AI is thinking…")
        self._status_label.setText("AI is thinking…")
        QTimer.singleShot(300, self._ttt_ai_move)

    def _ttt_ai_move(self) -> None:
        """AI (O) picks the best cell and places it."""
        if self._ttt_widget.is_game_over() or self._ttt_algo is None:
            return

        board = self._ttt_widget.board()
        cell = self._ttt_algo.get_best_move(board)

        if cell < 0:
            return

        self._ttt_widget.apply_move(cell, 2)   # 2 = O / AI

        if self._ttt_widget.is_game_over():
            self._ttt_game_ended()
        else:
            self._ttt_widget.set_human_turn(True)
            self._ttt_panel.set_status("Your turn — click a cell (X)")
            self._status_label.setText("Your turn (X)")

    def _ttt_game_ended(self) -> None:
        """Handle end-of-game: update score, show result."""
        winner = self._ttt_widget.winner()
        algo = self._algo_selector.get_algorithm_name()

        if winner == 1:
            msg = "🎉  You win!  Congratulations!"
            status = "You won this round!"
        elif winner == 2:
            msg = f"🤖  AI wins!  ({algo} played optimally)"
            status = "AI wins this round."
        else:
            msg = "🤝  It's a draw!"
            status = "Draw!"

        self._ttt_panel.add_result(winner)
        self._ttt_panel.set_status(msg)
        self._status_label.setText(status)
        self.statusBar().showMessage(status)

    # ── Graph Coloring handlers ───────────────────────────────────────

    def _gc_solve(self) -> None:
        """Run the selected GC algorithm and start step-by-step animation."""
        if self._gc_algo is None:
            return
        self._gc_timer.stop()
        self._gc_widget.reset()
        self._gc_panel.clear_selection()

        assignment, steps = self._gc_algo.solve(self._gc_current_graph)
        self._gc_steps = steps
        self._gc_step_idx = 0

        if not steps:
            self._gc_panel.set_status("No steps generated.")
            return

        algo_name = self._algo_selector.get_algorithm_name()
        self._gc_panel.set_status(f"Animating {len(steps)} steps…")
        self._status_label.setText(f"{algo_name}: {len(steps)} steps")
        self._gc_panel.set_solving(True)
        self._gc_update_timer_interval()
        self._gc_timer.start()

    def _gc_advance_step(self) -> None:
        """Called by timer — apply next step to the widget."""
        if self._gc_step_idx >= len(self._gc_steps):
            self._gc_timer.stop()
            self._gc_panel.set_solving(False)
            assignment = self._gc_widget.get_assignment()
            if self._gc_widget.is_complete() and not self._gc_widget.has_conflicts():
                self._gc_panel.set_status("✅ Solved! All regions colored.")
                self._status_label.setText("Graph colored successfully!")
            else:
                self._gc_panel.set_status("❌ No valid coloring found.")
                self._status_label.setText("Could not color the graph.")
            return

        action, node, color = self._gc_steps[self._gc_step_idx]
        self._gc_widget.apply_step(action, node, color)
        self._gc_step_idx += 1
        self._gc_panel.set_status(
            f"Step {self._gc_step_idx}/{len(self._gc_steps)}"
        )

    def _gc_reset(self) -> None:
        """Reset coloring but keep current graph."""
        self._gc_timer.stop()
        self._gc_steps = []
        self._gc_step_idx = 0
        self._gc_widget.reset()
        self._gc_panel.set_solving(False)
        self._gc_panel.clear_selection()
        self._gc_panel.set_status("Click a node to color manually\nor press Auto Solve")
        self._status_label.setText("Graph reset.")

    def _gc_random_graph(self) -> None:
        """Generate a new random graph and display it."""
        self._gc_timer.stop()
        self._gc_steps = []
        self._gc_step_idx = 0
        import random
        self._gc_current_graph = generate_random_graph(
            num_nodes=random.randint(6, 9)
        )
        self._gc_widget.set_graph(self._gc_current_graph)
        self._gc_panel.set_solving(False)
        self._gc_panel.clear_selection()
        self._gc_panel.set_status("New random graph — press Auto Solve")
        self._status_label.setText(
            f"Random graph: {self._gc_current_graph.num_nodes} nodes, "
            f"{len(self._gc_current_graph.edges)} edges"
        )

    def _gc_node_clicked(self, node_idx: int) -> None:
        """User clicked a node — prepare for manual color pick."""
        if not self._gc_current_graph:
            return
        name = self._gc_current_graph.names[node_idx]
        self._gc_panel.set_node_selected(node_idx, name)
        self._gc_panel.set_status(f"Node '{name}' selected — pick a color")

    def _gc_color_chosen(self, color_idx: int) -> None:
        """User clicked a color swatch — paint the selected node."""
        self._gc_widget.paint_selected(color_idx)
        # Check status after manual paint
        if self._gc_widget.is_complete():
            if not self._gc_widget.has_conflicts():
                self._gc_panel.set_status("✅ Correct! No conflicts.")
                self._status_label.setText("You solved it manually!")
            else:
                self._gc_panel.set_status("⚠️ Conflicts detected — keep going")
                self._status_label.setText("Some adjacent nodes share a color.")
        else:
            self._gc_panel.set_status("Click a node to color manually\nor press Auto Solve")

    def _gc_speed_changed(self, speed: float) -> None:
        self._gc_speed = speed
        if self._gc_timer.isActive():
            self._gc_update_timer_interval()

    def _gc_update_timer_interval(self) -> None:
        interval = max(20, int(180 / self._gc_speed))
        self._gc_timer.setInterval(interval)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._gc_timer.stop()
        self._stop_solver()
        super().closeEvent(event)


# ── Theme toggle button ──────────────────────────────────────────────────

class _ThemeToggleButton(QPushButton):
    """Pill-shaped button that shows the current theme and toggles it."""

    _LIGHT_STYLE = """
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #F5D66A, stop:1 #F5A623);
            color: #333;
            border-radius: 14px;
            font-size: 11px;
            font-weight: 700;
            padding: 0 10px;
            border: none;
            min-width: 90px;
            min-height: 28px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #FFE080, stop:1 #F5B530);
        }
    """
    _DARK_STYLE = """
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #2A3A5A, stop:1 #3A4A7A);
            color: #CDE;
            border-radius: 14px;
            font-size: 11px;
            font-weight: 700;
            padding: 0 10px;
            border: none;
            min-width: 90px;
            min-height: 28px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #3A4A7A, stop:1 #4A5A9A);
        }
    """

    def __init__(self, dark: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.set_dark(dark)

    def set_dark(self, dark: bool) -> None:
        if dark:
            self.setText("☀️  Light mode")
            self.setStyleSheet(self._DARK_STYLE)
            self.setToolTip("Switch to Light mode")
        else:
            self.setText("🌙  Dark mode")
            self.setStyleSheet(self._LIGHT_STYLE)
            self.setToolTip("Switch to Dark mode")
