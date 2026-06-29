from __future__ import annotations
from typing import List, Optional, Tuple
from models.state import State, GOAL_STATE


class Puzzle:

    def __init__(self, initial_board: Optional[Tuple[int, ...]] = None) -> None:
        """
        Initialize the puzzle.

        Args:
            initial_board: Initial board configuration. Uses goal if None.
        """
        board = initial_board if initial_board is not None else GOAL_STATE
        self.initial_state = State(board=board)
        self.current_state = self.initial_state
        self.goal_state = State(board=GOAL_STATE)
        self.history: List[State] = [self.initial_state]

    def reset(self) -> None:
        """Reset puzzle to initial state."""
        self.current_state = self.initial_state
        self.history = [self.initial_state]

    def set_board(self, board: Tuple[int, ...]) -> None:
        """
        Set a new board configuration.

        Args:
            board: New board as flat tuple.
        """
        self.initial_state = State(board=board)
        self.current_state = self.initial_state
        self.history = [self.initial_state]

    def apply_move(self, move: str) -> bool:
        """
        Apply a move to the current state.

        Args:
            move: Direction string ('U','D','L','R').

        Returns:
            True if move was valid and applied.
        """
        for neighbor in self.current_state.get_neighbors():
            if neighbor.move == move:
                self.current_state = neighbor
                self.history.append(neighbor)
                return True
        return False

    def apply_moves(self, moves: List[str]) -> List[State]:
        """
        Apply a sequence of moves from the initial state.

        Args:
            moves: List of move strings.

        Returns:
            List of states after each move.
        """
        self.reset()
        states = [self.current_state]
        for move in moves:
            self.apply_move(move)
            states.append(self.current_state)
        return states

    def is_solved(self) -> bool:
        """Check if the current state is the goal."""
        return self.current_state.is_goal()

    def is_solvable(self, board: Optional[Tuple[int, ...]] = None) -> bool:
        """
        Check if a given board configuration is solvable.
        Uses the inversion count method.

        Args:
            board: Board to check. Uses current state if None.

        Returns:
            True if the puzzle is solvable.
        """
        b = board if board is not None else self.current_state.board
        tiles = [x for x in b if x != 0]
        inversions = 0
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                if tiles[i] > tiles[j]:
                    inversions += 1
        # For 3x3, solvable iff inversions is even
        return inversions % 2 == 0

    @property
    def board(self) -> Tuple[int, ...]:
        """Get current board."""
        return self.current_state.board
