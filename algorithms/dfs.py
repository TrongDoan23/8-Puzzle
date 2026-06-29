from __future__ import annotations
from typing import Optional
from models.state import State
from algorithms.base import BaseAlgorithm

MAX_DEPTH = 50  # Limit depth to avoid infinite loops


class DFS(BaseAlgorithm):
    name = "DFS"
    category = "Uninformed Search"

    def _solve(self, initial: State, goal: State, heuristic=None) -> Optional[State]:
        stack = [initial]
        visited: set = {initial.board}
        self._generated = 1

        while stack:
            current = stack.pop()
            self._expanded += 1

            if current.board == goal.board:
                return current

            if current.depth >= MAX_DEPTH:
                continue

            for neighbor in reversed(current.get_neighbors()):
                if neighbor.board not in visited:
                    visited.add(neighbor.board)
                    stack.append(neighbor)
                    self._generated += 1

        return None
