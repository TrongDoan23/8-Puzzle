from __future__ import annotations
import math
import random
from typing import Optional, Callable
from models.state import State
from algorithms.base import BaseAlgorithm
from utils.heuristic import manhattan_distance


class SimulatedAnnealing(BaseAlgorithm):
    name = "Simulated Annealing"
    category = "Local Search"

    INITIAL_TEMP = 200.0
    COOLING_RATE = 0.9995
    MIN_TEMP = 0.001
    MAX_ITERATIONS = 100000

    def _solve(self, initial: State, goal: State, heuristic: Optional[Callable] = None) -> Optional[State]:
        h = heuristic or manhattan_distance
        current = initial
        best = initial
        best_score = h(initial.board, goal.board)
        temp = self.INITIAL_TEMP
        self._generated = 1

        for iteration in range(self.MAX_ITERATIONS):
            self._expanded += 1

            if current.board == goal.board:
                return current

            temp *= self.COOLING_RATE
            if temp < self.MIN_TEMP:
                break

            neighbors = current.get_neighbors()
            self._generated += len(neighbors)

            if not neighbors:
                break

            next_state = random.choice(neighbors)
            current_score = h(current.board, goal.board)
            next_score = h(next_state.board, goal.board)
            delta = current_score - next_score

            # Accept if better, or probabilistically if worse
            if delta > 0 or random.random() < math.exp(delta / temp):
                current = next_state
                if next_score < best_score:
                    best = next_state
                    best_score = next_score

        if best.board == goal.board:
            return best
        return None
