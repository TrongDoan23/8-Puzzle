from __future__ import annotations
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class SteepestAscent(BaseAlgorithm):
    name = "Steepest Ascent Hill Climbing"
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

            # Evaluate all neighbors
            scored = [(h(n.board, goal.board), n) for n in neighbors]
            scored.sort(key=lambda x: x[0])

            best_score, best = scored[0]
            current_score = h(current.board, goal.board)

            if best_score >= current_score:
                return None  # Local optimum

            current = best

        return None
