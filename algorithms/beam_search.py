from __future__ import annotations
from typing import Optional, Callable, List
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class BeamSearch(BaseAlgorithm):
    name = "Local Beam Search"
    category = "Local Search"
    BEAM_WIDTH = 3

    def _solve(self, initial: State, goal: State, heuristic: Optional[Callable] = None) -> Optional[State]:
        h = heuristic or manhattan_distance
        beam: List[State] = [initial]
        self._generated = 1
        visited: set = {initial.board}
        max_iterations = 10000

        for _ in range(max_iterations):
            if not beam:
                break

            # Check if any current state is goal
            for state in beam:
                self._expanded += 1
                if state.board == goal.board:
                    return state

            # Generate all successors
            all_successors: List[State] = []
            for state in beam:
                for neighbor in state.get_neighbors():
                    if neighbor.board not in visited:
                        visited.add(neighbor.board)
                        all_successors.append(neighbor)
                        self._generated += 1

            if not all_successors:
                break

            # Keep k best successors
            all_successors.sort(key=lambda s: h(s.board, goal.board))
            beam = all_successors[:self.BEAM_WIDTH]

        return None
