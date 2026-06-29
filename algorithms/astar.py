from __future__ import annotations
import heapq
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class AStar(BaseAlgorithm):
    name = "A*"
    category = "Informed Search"

    def _solve(self, initial: State, goal: State, heuristic: Optional[Callable] = None) -> Optional[State]:
        h = heuristic or manhattan_distance
        counter = 0
        h_val = h(initial.board, goal.board)
        f_val = initial.cost + h_val
        frontier: list = [(f_val, counter, initial)]
        visited: dict = {initial.board: f_val}
        self._generated = 1

        while frontier:
            f, _, current = heapq.heappop(frontier)
            self._expanded += 1

            if current.board == goal.board:
                return current

            if f > visited.get(current.board, float('inf')):
                continue

            for neighbor in current.get_neighbors():
                h_val = h(neighbor.board, goal.board)
                new_f = neighbor.cost + h_val
                if new_f < visited.get(neighbor.board, float('inf')):
                    visited[neighbor.board] = new_f
                    counter += 1
                    heapq.heappush(frontier, (new_f, counter, neighbor))
                    self._generated += 1

        return None
