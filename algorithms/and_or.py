from __future__ import annotations
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class AndOrSearch(BaseAlgorithm):
    name = "AND-OR Graph Search"
    category = "Partial Observable Search"
    MAX_DEPTH = 35

    def _solve(
        self,
        initial: State,
        goal: State,
        heuristic: Optional[Callable] = None,
    ) -> Optional[State]:
        h = heuristic or manhattan_distance

        # Iterative DFS with explicit ancestor tracking
        # Stack entry: (state, ancestors_frozenset)
        stack = [(initial, frozenset())]
        self._generated = 1

        while stack:
            state, ancestors = stack.pop()

            # Cycle / depth guard
            if state.board in ancestors:
                continue
            if state.depth > self.MAX_DEPTH:
                continue

            self._expanded += 1

            if state.board == goal.board:
                return state

            new_ancestors = ancestors | {state.board}

            # Generate children sorted by heuristic (best last so they
            # are popped first from the stack — LIFO order)
            children = state.get_neighbors()
            self._generated += len(children)
            # Sort worst-first so best is on top of stack
            children.sort(
                key=lambda s: h(s.board, goal.board),
                reverse=True,
            )

            for child in children:
                if child.board not in new_ancestors:
                    stack.append((child, new_ancestors))

        return None
