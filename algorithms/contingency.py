from __future__ import annotations
from typing import Optional, Callable, Dict
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class ContingencySearch(BaseAlgorithm):
    name = "Contingency Search"
    category = "Partial Observable Search"
    MAX_STEPS = 2000
    REVISIT_PENALTY = 4      # cost added per revisit
    MAX_PENALTY     = 20     # cap so the agent can always escape
    LOOKAHEAD_DEPTH = 8      # A* lookahead depth when greedy stalls

    def _solve(
        self, initial: State, goal: State, heuristic: Optional[Callable] = None
    ) -> Optional[State]:
        h = heuristic or manhattan_distance
        current = initial
        self._generated = 1
        visit_count: Dict = {}
        stall_streak = 0          # steps without heuristic improvement

        for _ in range(self.MAX_STEPS):
            self._expanded += 1

            if current.board == goal.board:
                return current

            neighbors = current.get_neighbors()
            self._generated += len(neighbors)

            # Score each neighbor: heuristic + capped revisit penalty
            def score(s: State) -> float:
                penalty = min(
                    visit_count.get(s.board, 0) * self.REVISIT_PENALTY,
                    self.MAX_PENALTY,
                )
                return h(s.board, goal.board) + penalty

            current_h = h(current.board, goal.board)
            best = min(neighbors, key=score)

            # Check if we're stalling (no improvement for several steps)
            if score(best) >= current_h + self.REVISIT_PENALTY:
                stall_streak += 1
            else:
                stall_streak = 0

            # Contingency: if stalled, use a short A* lookahead to escape
            if stall_streak >= 4:
                escape = self._lookahead(current, goal, h, self.LOOKAHEAD_DEPTH)
                if escape is not None:
                    current = escape
                    stall_streak = 0
                    continue

            visit_count[current.board] = visit_count.get(current.board, 0) + 1
            current = best

        return None

    def _lookahead(
        self,
        start: State,
        goal: State,
        h: Callable,
        depth: int,
    ) -> Optional[State]:
        """
        Short A* search limited to `depth` moves.
        Returns the NEXT state to move to (one step from start),
        chosen by the best path found within the depth limit.
        """
        import heapq
        counter = 0
        f0 = h(start.board, goal.board)
        # (f, counter, state, first_step_state)
        frontier = [(f0, counter, start, None)]
        visited: Dict = {start.board: 0}
        best_terminal = None
        best_first = None

        while frontier:
            f, _, current, first_step = heapq.heappop(frontier)

            if current.board == goal.board:
                return first_step or current

            if current.depth - start.depth >= depth:
                # Track best terminal for fallback
                if best_terminal is None or h(current.board, goal.board) < h(
                    best_terminal.board, goal.board
                ):
                    best_terminal = current
                    best_first = first_step
                continue

            for nb in current.get_neighbors():
                nf = (nb.depth - start.depth) + h(nb.board, goal.board)
                if nf < visited.get(nb.board, float("inf")):
                    visited[nb.board] = nf
                    counter += 1
                    fs = first_step if first_step is not None else nb
                    heapq.heappush(frontier, (nf, counter, nb, fs))

        return best_first
