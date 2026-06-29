from __future__ import annotations
import heapq
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class Greedy(BaseAlgorithm):
    name = "Greedy"
    category = "Informed Search"

    def _solve(self, initial: State, goal: State, heuristic: Optional[Callable] = None) -> Optional[State]:
        h = heuristic or manhattan_distance
        counter = 0
        h_val = h(initial.board, goal.board)
        frontier: list = [(h_val, counter, initial)]
        visited: set = {initial.board}
        self._generated = 1

        while frontier:
            _, _, current = heapq.heappop(frontier)
            self._expanded += 1

            if current.board == goal.board:
                return current

            for neighbor in current.get_neighbors():
                if neighbor.board not in visited:
                    visited.add(neighbor.board)
                    h_val = h(neighbor.board, goal.board)
                    counter += 1
                    heapq.heappush(frontier, (h_val, counter, neighbor))
                    self._generated += 1

        return None
