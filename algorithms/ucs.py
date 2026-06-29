from __future__ import annotations
import heapq
from typing import Optional
from models.state import State
from algorithms.base import BaseAlgorithm


class UCS(BaseAlgorithm):
    name = "UCS"
    category = "Uninformed Search"

    def _solve(self, initial: State, goal: State, heuristic=None) -> Optional[State]:
        # Priority queue: (cost, counter, state)
        counter = 0
        frontier: list = [(0, counter, initial)]
        visited: dict = {initial.board: 0}
        self._generated = 1

        while frontier:
            cost, _, current = heapq.heappop(frontier)
            self._expanded += 1

            if current.board == goal.board:
                return current

            if cost > visited.get(current.board, float('inf')):
                continue

            for neighbor in current.get_neighbors():
                new_cost = neighbor.cost
                if new_cost < visited.get(neighbor.board, float('inf')):
                    visited[neighbor.board] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, neighbor))
                    self._generated += 1

        return None
