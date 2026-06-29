from __future__ import annotations
import random
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class StochasticHC(BaseAlgorithm):
    name = "Stochastic Hill Climbing"
    category = "Local Search"
    MAX_RESTARTS = 30
    MAX_STEPS = 500

    def _solve(
        self, initial: State, goal: State, heuristic: Optional[Callable] = None
    ) -> Optional[State]:
        h = heuristic or manhattan_distance
        self._generated = 1

        result = self._run(initial, goal, h)
        if result is not None:
            return result

        from utils.random_board import generate_random_board
        for _ in range(self.MAX_RESTARTS - 1):
            new_board = generate_random_board(num_moves=30)
            start = State(board=new_board)
            result = self._run(start, goal, h)
            if result is not None:
                return result

        return None

    def _run(
        self, initial: State, goal: State, h: Callable
    ) -> Optional[State]:
        """Single stochastic hill-climbing attempt from initial."""
        current = initial
        for _ in range(self.MAX_STEPS):
            self._expanded += 1
            if current.board == goal.board:
                return current

            neighbors = current.get_neighbors()
            self._generated += len(neighbors)

            current_score = h(current.board, goal.board)
            improving = [n for n in neighbors if h(n.board, goal.board) < current_score]

            if not improving:
                return None   # local optimum on this run

            current = random.choice(improving)

        return None
