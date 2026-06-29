from __future__ import annotations
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm


class Backtracking(BaseAlgorithm):
    name = "Backtracking"
    category = "CSP / Constraint Search"
    MAX_DEPTH = 30

    def _solve(
        self,
        initial: State,
        goal: State,
        heuristic: Optional[Callable] = None,
    ) -> Optional[State]:
        # Stack entry: (state, path_frozenset_of_ancestors)
        stack = [(initial, frozenset())]
        self._generated = 1

        while stack:
            current, ancestors = stack.pop()

            if current.board in ancestors:
                continue
            if current.depth > self.MAX_DEPTH:
                continue

            self._expanded += 1

            if current.board == goal.board:
                return current

            new_ancestors = ancestors | {current.board}

            # Push children in reverse order so first child is tried first
            for neighbor in reversed(current.get_neighbors()):
                if neighbor.board not in new_ancestors:
                    self._generated += 1
                    stack.append((neighbor, new_ancestors))

        return None
