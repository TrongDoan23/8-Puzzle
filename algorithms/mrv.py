from __future__ import annotations
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class MRV(BaseAlgorithm):
    name = "MRV"
    category = "CSP / Constraint Search"
    MAX_DEPTH = 30

    def _solve(
        self,
        initial: State,
        goal: State,
        heuristic: Optional[Callable] = None,
    ) -> Optional[State]:
        h = heuristic or manhattan_distance

        # Stack entry: (state, ancestors_frozenset)
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

            neighbors = [
                n for n in current.get_neighbors()
                if n.board not in new_ancestors
            ]
            self._generated += len(neighbors)

            if not neighbors:
                continue

            # MRV key: (num_successors_of_child, h_value)
            # Sort worst-last so best is popped first (stack is LIFO)
            def mrv_key(s: State) -> tuple:
                successors = sum(
                    1 for nb in s.get_neighbors()
                    if nb.board not in new_ancestors
                )
                return (successors, h(s.board, goal.board))

            neighbors.sort(key=mrv_key, reverse=True)  # worst last → best on top

            for neighbor in neighbors:
                stack.append((neighbor, new_ancestors))

        return None
