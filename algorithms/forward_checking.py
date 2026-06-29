from __future__ import annotations
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class ForwardChecking(BaseAlgorithm):
    name = "Forward Checking"
    category = "CSP / Constraint Search"
    MAX_DEPTH = 30

    def _solve(
        self,
        initial: State,
        goal: State,
        heuristic: Optional[Callable] = None,
    ) -> Optional[State]:
        h = heuristic or manhattan_distance
        # Initial bound: loose enough to find a solution
        bound = h(initial.board, goal.board) + 30

        # Stack entry: (state, ancestors_frozenset, current_bound)
        stack = [(initial, frozenset(), bound)]
        self._generated = 1

        while stack:
            current, ancestors, cur_bound = stack.pop()

            if current.board in ancestors:
                continue
            if current.depth > self.MAX_DEPTH:
                continue

            f = current.cost + h(current.board, goal.board)
            if f > cur_bound:
                continue

            self._expanded += 1

            if current.board == goal.board:
                return current

            new_ancestors = ancestors | {current.board}

            children = current.get_neighbors()
            # Forward checking: prune children exceeding the bound
            valid = [
                n for n in children
                if n.board not in new_ancestors
                and (n.cost + h(n.board, goal.board)) <= cur_bound
            ]
            self._generated += len(valid)

            # Sort worst-last (best h on top of stack — LIFO)
            valid.sort(key=lambda s: h(s.board, goal.board), reverse=True)

            for neighbor in valid:
                stack.append((neighbor, new_ancestors, cur_bound))

        return None
