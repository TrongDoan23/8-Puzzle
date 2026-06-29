from __future__ import annotations
import heapq
from typing import Optional, Callable, Dict, Set, Tuple as PyTuple
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class AC3(BaseAlgorithm):
    name = "AC-3"
    category = "CSP / Constraint Search"

    def _solve(
        self, initial: State, goal: State, heuristic: Optional[Callable] = None
    ) -> Optional[State]:
        # Use manhattan + linear-conflict penalty (AC-3 constraint effect)
        from utils.heuristic import linear_conflict
        h = linear_conflict   # already incorporates constraint reasoning

        counter = 0
        h0 = h(initial.board, goal.board)
        frontier: list = [(h0, counter, initial)]
        visited: Dict = {initial.board: h0}
        self._generated = 1

        while frontier:
            f, _, current = heapq.heappop(frontier)
            self._expanded += 1

            if current.board == goal.board:
                return current

            if f > visited.get(current.board, float("inf")):
                continue

            for neighbor in current.get_neighbors():
                # Arc-consistency penalty: extra cost for states where
                # tiles conflict with each other in their row/column.
                conflict_penalty = self._arc_violation_cost(neighbor, goal)
                h_val = h(neighbor.board, goal.board)
                new_f = neighbor.cost + h_val + conflict_penalty

                if new_f < visited.get(neighbor.board, float("inf")):
                    visited[neighbor.board] = new_f
                    counter += 1
                    heapq.heappush(frontier, (new_f, counter, neighbor))
                    self._generated += 1

        return None

    # ------------------------------------------------------------------

    def _arc_violation_cost(self, state: State, goal: State) -> int:
        """
        Count arc violations: pairs of tiles (ti, tj) that are in their
        goal row/column but in the wrong relative order — a direct
        linear-conflict indicator.  Returns 0 or 2 per conflict pair.
        """
        board = state.board
        goal_board = goal.board

        # Build goal position map
        goal_pos: Dict[int, PyTuple[int, int]] = {}
        for idx, tile in enumerate(goal_board):
            goal_pos[tile] = divmod(idx, 3)

        violations = 0

        # Row conflicts
        for row in range(3):
            in_row = [
                (board[row * 3 + col], col, goal_pos[board[row * 3 + col]][1])
                for col in range(3)
                if board[row * 3 + col] != 0
                and goal_pos[board[row * 3 + col]][0] == row
            ]
            for i in range(len(in_row)):
                for j in range(i + 1, len(in_row)):
                    _, ci, gi = in_row[i]
                    _, cj, gj = in_row[j]
                    if (ci < cj) != (gi < gj):
                        violations += 2

        # Column conflicts
        for col in range(3):
            in_col = [
                (board[row * 3 + col], row, goal_pos[board[row * 3 + col]][0])
                for row in range(3)
                if board[row * 3 + col] != 0
                and goal_pos[board[row * 3 + col]][1] == col
            ]
            for i in range(len(in_col)):
                for j in range(i + 1, len(in_col)):
                    _, ri, gi = in_col[i]
                    _, rj, gj = in_col[j]
                    if (ri < rj) != (gi < gj):
                        violations += 2

        return violations
