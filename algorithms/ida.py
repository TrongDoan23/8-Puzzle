from __future__ import annotations
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class IDAStar(BaseAlgorithm):
    name = "IDA*"
    category = "Informed Search"

    def _solve(
        self,
        initial: State,
        goal: State,
        heuristic: Optional[Callable] = None,
    ) -> Optional[State]:
        h = heuristic or manhattan_distance
        threshold = h(initial.board, goal.board)

        for _ in range(500):           # at most 500 threshold raises
            result, next_t = self._dfs(initial, goal, h, threshold)
            if result is not None:
                return result
            if next_t == float("inf"):
                return None            # exhausted
            if next_t <= threshold:
                return None            # no progress guard
            threshold = next_t

        return None

    # ------------------------------------------------------------------

    def _dfs(
        self,
        initial: State,
        goal: State,
        h: Callable,
        threshold: float,
    ) -> tuple:
        """
        One threshold-bounded DFS pass.

        Returns (goal_state, 0) on success, or (None, min_exceeded_f).
        Uses an explicit stack: each entry is
            (state, g_cost, ancestors_frozenset)
        """
        min_exceeded = float("inf")

        # Stack items: (state, g, ancestors)
        stack = [(initial, 0, frozenset())]

        while stack:
            state, g, ancestors = stack.pop()

            # Skip if already on current path (cycle)
            if state.board in ancestors:
                continue

            f = g + h(state.board, goal.board)

            if f > threshold:
                if f < min_exceeded:
                    min_exceeded = f
                continue

            self._expanded += 1

            if state.board == goal.board:
                return state, 0

            new_ancestors = ancestors | {state.board}

            # Expand children — push in reverse-heuristic order so the
            # best child is on top of the stack (lowest h popped first).
            children = [
                nb for nb in state.get_neighbors()
                if nb.board not in new_ancestors
            ]
            self._generated += len(children)

            # Sort worst-first (reverse) so best child ends up on top
            children.sort(
                key=lambda nb: (g + 1) + h(nb.board, goal.board),
                reverse=True,
            )

            for child in children:
                stack.append((child, g + 1, new_ancestors))

        return None, min_exceeded
