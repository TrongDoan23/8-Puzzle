from __future__ import annotations
from collections import deque
from typing import Optional
from models.state import State
from algorithms.base import BaseAlgorithm


class BFS(BaseAlgorithm):
    name = "BFS"
    category = "Uninformed Search"

    def _solve(self, initial: State, goal: State, heuristic=None) -> Optional[State]:
        if initial == goal:
            return initial

        frontier: deque[State] = deque([initial])
        visited: set = {initial.board}
        self._generated = 1

        while frontier:
            current = frontier.popleft()
            self._expanded += 1

            for neighbor in current.get_neighbors():
                if neighbor.board == goal.board:
                    self._generated += 1
                    return neighbor
                if neighbor.board not in visited:
                    visited.add(neighbor.board)
                    frontier.append(neighbor)
                    self._generated += 1

        return None
