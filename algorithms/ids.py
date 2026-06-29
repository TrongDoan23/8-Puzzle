from __future__ import annotations
from typing import Optional
from models.state import State
from algorithms.base import BaseAlgorithm


class IDS(BaseAlgorithm):
    name = "IDS"
    category = "Uninformed Search"

    def _solve(self, initial: State, goal: State, heuristic=None) -> Optional[State]:
        self._generated = 1
        for depth_limit in range(0, 200):
            result = self._dls(initial, goal, depth_limit)
            if result is not None:
                return result
        return None

    def _dls(self, initial: State, goal: State, limit: int) -> Optional[State]:
        # Stack entries: (state, ancestors_frozenset)
        # ancestors tracks boards on the current path to avoid cycles.
        stack = [(initial, frozenset())]

        while stack:
            current, ancestors = stack.pop()

            if current.board in ancestors:
                continue

            self._expanded += 1

            if current.board == goal.board:
                return current

            if current.depth >= limit:
                continue

            new_ancestors = ancestors | {current.board}

            for neighbor in reversed(current.get_neighbors()):
                if neighbor.board not in new_ancestors:
                    self._generated += 1
                    stack.append((neighbor, new_ancestors))

        return None
