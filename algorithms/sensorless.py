from __future__ import annotations
from typing import Optional, Callable, FrozenSet, List, Tuple
from collections import deque
from models.state import State, GOAL_STATE
from algorithms.base import BaseAlgorithm


class SensorlessSearch(BaseAlgorithm):
    name = "Sensorless Search"
    category = "Partial Observable Search"
    MAX_BELIEF_STATES = 3   # keep small so BFS stays tractable
    MAX_QUEUE = 8000

    def _solve(
        self, initial: State, goal: State, heuristic: Optional[Callable] = None
    ) -> Optional[State]:
        goal_board = goal.board

        # Build initial belief (only boards that are different from goal)
        perturbations: List[tuple] = []
        for nb in initial.get_neighbors():
            if nb.board != goal_board:
                perturbations.append(nb.board)
                if len(perturbations) >= self.MAX_BELIEF_STATES - 1:
                    break

        init_belief = frozenset([initial.board] + perturbations)
        self._generated = 1

        # Queue entry: (belief, real_state_with_parent_chain)
        queue: deque[Tuple[FrozenSet, State]] = deque(
            [(init_belief, initial)]
        )
        visited: set = {init_belief}

        steps = 0
        while queue and steps < self.MAX_QUEUE:
            belief, real_state = queue.popleft()
            self._expanded += 1
            steps += 1

            # Success: ALL boards in belief are at goal
            if all(b == goal_board for b in belief):
                if real_state.board == goal_board:
                    return real_state
                # Real board reached goal but State pointer didn't update —
                # shouldn't happen, but guard anyway
                break

            for action in ['U', 'D', 'L', 'R']:
                new_belief = self._apply_action(belief, action)
                if new_belief not in visited:
                    visited.add(new_belief)
                    # Advance real state if action is applicable
                    new_real = real_state
                    for nb in real_state.get_neighbors():
                        if nb.move == action:
                            new_real = nb
                            break
                    queue.append((new_belief, new_real))
                    self._generated += 1

        # Fallback: if sensorless BFS can't converge belief fully within
        # budget, return None so the GUI shows "No solution found"
        return None

    def _apply_action(self, belief: FrozenSet, action: str) -> FrozenSet:
        """Apply action to every board; boards where it's invalid stay put."""
        new_boards = set()
        for board in belief:
            s = State(board=board)
            moved = False
            for nb in s.get_neighbors():
                if nb.move == action:
                    new_boards.add(nb.board)
                    moved = True
                    break
            if not moved:
                new_boards.add(board)
        return frozenset(new_boards)
