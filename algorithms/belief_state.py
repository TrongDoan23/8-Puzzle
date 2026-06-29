from __future__ import annotations
from typing import Optional, Callable, List
from models.state import State, GOAL_STATE
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class BeliefStateSearch(BaseAlgorithm):
    name = "Belief State Search"
    category = "Partial Observable Search"
    MAX_BELIEF_SIZE = 5
    MAX_STEPS = 3000

    def _solve(
        self, initial: State, goal: State, heuristic: Optional[Callable] = None
    ) -> Optional[State]:
        h = heuristic or manhattan_distance

        # Belief set: real board + nearby perturbations
        belief: List[tuple] = [initial.board]
        for nb in initial.get_neighbors()[: self.MAX_BELIEF_SIZE - 1]:
            belief.append(nb.board)

        self._generated = len(belief)

        # real_state is the State with proper parent chain for reconstruction
        real_state = initial

        for _ in range(self.MAX_STEPS):
            self._expanded += 1

            if real_state.board == goal.board:
                return real_state

            neighbors = real_state.get_neighbors()
            self._generated += len(neighbors)

            if not neighbors:
                break

            # Score each action by average heuristic over belief set
            best_nb: Optional[State] = None
            best_score = float("inf")

            for nb in neighbors:
                new_belief = self._apply_to_belief(belief, nb.move)
                avg_h = sum(h(b, goal.board) for b in new_belief) / len(new_belief)
                if avg_h < best_score:
                    best_score = avg_h
                    best_nb = nb

            if best_nb is None:
                break

            # Advance belief and real state
            belief = self._apply_to_belief(belief, best_nb.move)
            real_state = best_nb

        return None

    def _apply_to_belief(self, belief: List[tuple], action: str) -> List[tuple]:
        """Apply `action` to every board in the belief set."""
        result = []
        for board in belief:
            s = State(board=board)
            moved = False
            for nb in s.get_neighbors():
                if nb.move == action:
                    result.append(nb.board)
                    moved = True
                    break
            if not moved:
                result.append(board)
        return result
