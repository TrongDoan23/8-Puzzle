from __future__ import annotations
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm, SolveResult
from utils.heuristic import manhattan_distance


class HillClimbing(BaseAlgorithm):
    name = "Hill Climbing"
    category = "Local Search"

    def _solve(self, initial: State, goal: State, heuristic: Optional[Callable] = None) -> Optional[State]:
        h = heuristic or manhattan_distance
        current = initial
        self._generated = 1
        max_iterations = 10000

        for _ in range(max_iterations):
            self._expanded += 1
            if current.board == goal.board:
                return current

            neighbors = current.get_neighbors()
            self._generated += len(neighbors)

            best = min(neighbors, key=lambda s: h(s.board, goal.board))
            if h(best.board, goal.board) >= h(current.board, goal.board):
                # Local optimum — cannot improve
                return None

            current = best

        return None
