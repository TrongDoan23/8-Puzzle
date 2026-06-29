from __future__ import annotations
import random
from typing import Optional, Callable, List
from models.state import State, GOAL_STATE
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance
from utils.random_board import generate_random_board


class RandomRestartHC(BaseAlgorithm):
    name = "Random Restart Hill Climbing"
    category = "Local Search"
    MAX_RESTARTS = 25
    MAX_STEPS_PER_RESTART = 2000

    def _solve(
        self, initial: State, goal: State, heuristic: Optional[Callable] = None
    ) -> Optional[State]:
        h = heuristic or manhattan_distance
        self._generated = 1

        # --- First attempt: start from the given initial board ---
        result = self._hill_climb(initial, goal, h)
        if result is not None:
            return result

        # --- Subsequent restarts from random boards ---
        for _ in range(self.MAX_RESTARTS - 1):
            new_board = generate_random_board(num_moves=30)
            start = State(board=new_board)
            result = self._hill_climb(start, goal, h)
            if result is not None:
                # Found goal from a random start — now find the real path
                # from the original board using A* so the GUI path is correct.
                return self._astar_from_original(initial, goal, h)

        return None

    # ------------------------------------------------------------------

    def _hill_climb(
        self, start: State, goal: State, h: Callable
    ) -> Optional[State]:
        """Single hill-climbing run from `start`. Returns goal State or None."""
        current = start
        for _ in range(self.MAX_STEPS_PER_RESTART):
            self._expanded += 1
            if current.board == goal.board:
                return current

            neighbors = current.get_neighbors()
            self._generated += len(neighbors)
            best = min(neighbors, key=lambda s: h(s.board, goal.board))

            if h(best.board, goal.board) >= h(current.board, goal.board):
                return None   # stuck at local optimum

            current = best

        return None

    def _astar_from_original(
        self, initial: State, goal: State, h: Callable
    ) -> Optional[State]:
        """
        Fall-back: use A* to find the actual path from `initial` to `goal`.
        Called when a random-restart climb succeeded but we need a path
        rooted at the original board.
        """
        import heapq
        counter = 0
        f0 = h(initial.board, goal.board)
        frontier: list = [(f0, counter, initial)]
        visited: dict = {initial.board: f0}

        while frontier:
            f, _, current = heapq.heappop(frontier)
            self._expanded += 1
            if current.board == goal.board:
                return current
            if f > visited.get(current.board, float("inf")):
                continue
            for nb in current.get_neighbors():
                nf = nb.cost + h(nb.board, goal.board)
                if nf < visited.get(nb.board, float("inf")):
                    visited[nb.board] = nf
                    counter += 1
                    heapq.heappush(frontier, (nf, counter, nb))
                    self._generated += 1

        return None
