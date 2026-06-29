from __future__ import annotations
from typing import Optional, Tuple
from algorithms.base import BaseAlgorithm, SolveResult
from models.state import GOAL_STATE


class Minimax(BaseAlgorithm):
    name = "Minimax"
    category = "Adversarial Search"

    # Sentinel so MainWindow knows this is a TTT algorithm
    is_ttt_algorithm = True

    def solve(self, initial, goal=GOAL_STATE, heuristic=None) -> SolveResult:
        return SolveResult.not_applicable("Tic-Tac-Toe mode")

    def _solve(self, initial, goal, heuristic=None):
        return None

    def get_best_move(self, board: list) -> int:
        """
        Given a 9-element board (0=empty, 1=X/human, 2=O/AI),
        return the best cell index for the AI (O).
        """
        best_score = -1000
        best_move = -1
        for i in range(9):
            if board[i] == 0:
                board[i] = 2
                score = self._minimax(board, 0, False)
                board[i] = 0
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move

    def _minimax(self, board: list, depth: int, is_maximizing: bool) -> int:
        winner = _check_winner(board)
        if winner == 2:
            return 10 - depth
        if winner == 1:
            return depth - 10
        if all(c != 0 for c in board):
            return 0

        if is_maximizing:
            best = -1000
            for i in range(9):
                if board[i] == 0:
                    board[i] = 2
                    best = max(best, self._minimax(board, depth + 1, False))
                    board[i] = 0
            return best
        else:
            best = 1000
            for i in range(9):
                if board[i] == 0:
                    board[i] = 1
                    best = min(best, self._minimax(board, depth + 1, True))
                    board[i] = 0
            return best


class AlphaBeta(BaseAlgorithm):
    name = "Alpha Beta"
    category = "Adversarial Search"
    is_ttt_algorithm = True

    def solve(self, initial, goal=GOAL_STATE, heuristic=None) -> SolveResult:
        return SolveResult.not_applicable("Tic-Tac-Toe mode")

    def _solve(self, initial, goal, heuristic=None):
        return None

    def get_best_move(self, board: list) -> int:
        """Return the best cell index for the AI using alpha-beta pruning."""
        best_score = -1000
        best_move = -1
        for i in range(9):
            if board[i] == 0:
                board[i] = 2
                score = self._alphabeta(board, 0, -1000, 1000, False)
                board[i] = 0
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move

    def _alphabeta(
        self, board: list, depth: int, alpha: int, beta: int, is_maximizing: bool
    ) -> int:
        winner = _check_winner(board)
        if winner == 2:
            return 10 - depth
        if winner == 1:
            return depth - 10
        if all(c != 0 for c in board):
            return 0

        if is_maximizing:
            best = -1000
            for i in range(9):
                if board[i] == 0:
                    board[i] = 2
                    best = max(best, self._alphabeta(board, depth + 1, alpha, beta, False))
                    board[i] = 0
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break
            return best
        else:
            best = 1000
            for i in range(9):
                if board[i] == 0:
                    board[i] = 1
                    best = min(best, self._alphabeta(board, depth + 1, alpha, beta, True))
                    board[i] = 0
                    beta = min(beta, best)
                    if beta <= alpha:
                        break
            return best


class Expectiminimax(BaseAlgorithm):
    name = "Expectiminimax"
    category = "Adversarial Search"
    is_ttt_algorithm = True
    RANDOM_CHANCE = 0.15   # probability of random move (makes it beatable)

    def solve(self, initial, goal=GOAL_STATE, heuristic=None) -> SolveResult:
        return SolveResult.not_applicable("Tic-Tac-Toe mode")

    def _solve(self, initial, goal, heuristic=None):
        return None

    def get_best_move(self, board: list) -> int:
        """
        Return a move using expectiminimax.
        With RANDOM_CHANCE probability, picks a random valid move.
        """
        import random
        empty = [i for i in range(9) if board[i] == 0]
        if not empty:
            return -1

        if random.random() < self.RANDOM_CHANCE:
            return random.choice(empty)

        best_score = -1000
        best_move = empty[0]
        for i in empty:
            board[i] = 2
            score = self._expectiminimax(board, 0, False)
            board[i] = 0
            if score > best_score:
                best_score = score
                best_move = i
        return best_move

    def _expectiminimax(self, board: list, depth: int, is_maximizing: bool) -> float:
        winner = _check_winner(board)
        if winner == 2:
            return 10 - depth
        if winner == 1:
            return depth - 10
        if all(c != 0 for c in board):
            return 0

        empty = [i for i in range(9) if board[i] == 0]
        if not empty:
            return 0

        if is_maximizing:
            # Chance node: weighted average between best and random
            best_val = -1000
            for i in empty:
                board[i] = 2
                val = self._expectiminimax(board, depth + 1, False)
                board[i] = 0
                best_val = max(best_val, val)
            random_val = sum(
                self._expectiminimax(
                    (lambda b, idx: (b.__setitem__(idx, 2), b)[1])(board[:], i),
                    depth + 1, False
                )
                for i in empty
            ) / len(empty)
            # Weighted: (1-p)*best + p*random
            return (1 - self.RANDOM_CHANCE) * best_val + self.RANDOM_CHANCE * random_val
        else:
            best_val = 1000
            for i in empty:
                board[i] = 1
                val = self._expectiminimax(board, depth + 1, True)
                board[i] = 0
                best_val = min(best_val, val)
            return best_val


# ── Shared helper ────────────────────────────────────────────────────────

WINNING_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # cols
    (0, 4, 8), (2, 4, 6),               # diagonals
]


def _check_winner(board: list) -> int:
    """Return 1 (X wins), 2 (O wins), or 0 (no winner yet)."""
    for a, b, c in WINNING_LINES:
        if board[a] != 0 and board[a] == board[b] == board[c]:
            return board[a]
    return 0
