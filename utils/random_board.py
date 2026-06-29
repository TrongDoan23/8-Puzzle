from __future__ import annotations
import random
from typing import Tuple
from models.state import State, GOAL_STATE


def generate_random_board(num_moves: int = 50) -> Tuple[int, ...]:
    """
    Generate a random solvable board by starting from the goal state
    and making random moves. This guarantees solvability.

    Args:
        num_moves: Number of random moves to make from goal state.
                   Higher = more shuffled.

    Returns:
        A solvable board configuration (never equals goal state).
    """
    board = GOAL_STATE

    # Keep shuffling until we get a board that's not the goal
    while True:
        current = list(board)
        state = State(board=tuple(current))

        for _ in range(num_moves):
            neighbors = state.get_neighbors()
            # Avoid immediately reversing last move for better shuffling
            if state.move:
                reverse = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}
                neighbors = [
                    n for n in neighbors
                    if n.move != reverse.get(state.move)
                ] or neighbors
            state = random.choice(neighbors)
            state = State(board=state.board)  # detach parent chain

        if state.board != GOAL_STATE:
            return state.board
