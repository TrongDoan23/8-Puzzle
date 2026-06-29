from __future__ import annotations
from typing import List, Optional, Tuple


GOAL_STATE: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Direction constants
DIRECTIONS = {
    'U': -3,  # Move blank up (blank moves up, tile comes down)
    'D': 3,   # Move blank down
    'L': -1,  # Move blank left
    'R': 1,   # Move blank right
}

DIRECTION_NAMES = {
    'U': 'Up',
    'D': 'Down',
    'L': 'Left',
    'R': 'Right',
}


class State:
    """
    Represents a single state of the 8-Puzzle board.
    The board is stored as a flat tuple of 9 integers (0 = blank).
    """

    def __init__(
        self,
        board: Tuple[int, ...],
        parent: Optional['State'] = None,
        move: Optional[str] = None,
        cost: int = 0,
        depth: int = 0,
    ) -> None:
        """
        Initialize a puzzle state.

        Args:
            board: Flat tuple of 9 integers, 0 represents blank.
            parent: Parent state (None for initial state).
            move: The move that led to this state ('U','D','L','R').
            cost: Path cost from initial state.
            depth: Depth in search tree.
        """
        self.board = board
        self.parent = parent
        self.move = move
        self.cost = cost
        self.depth = depth
        self._blank_index: Optional[int] = None

    @property
    def blank_index(self) -> int:
        """Get the index of the blank tile (0)."""
        if self._blank_index is None:
            self._blank_index = self.board.index(0)
        return self._blank_index

    def is_goal(self) -> bool:
        """Check if this state is the goal state."""
        return self.board == GOAL_STATE

    def get_neighbors(self) -> List['State']:
        """
        Generate all valid neighboring states.

        Returns:
            List of valid State objects reachable in one move.
        """
        neighbors = []
        blank = self.blank_index
        row, col = divmod(blank, 3)

        moves = []
        if row > 0:
            moves.append('U')
        if row < 2:
            moves.append('D')
        if col > 0:
            moves.append('L')
        if col < 2:
            moves.append('R')

        for move in moves:
            new_blank = blank + DIRECTIONS[move]
            new_board = list(self.board)
            new_board[blank], new_board[new_blank] = new_board[new_blank], new_board[blank]
            neighbors.append(State(
                board=tuple(new_board),
                parent=self,
                move=move,
                cost=self.cost + 1,
                depth=self.depth + 1,
            ))

        return neighbors

    def get_path(self) -> List[str]:
        """
        Reconstruct the path of moves from initial state to this state.

        Returns:
            List of move strings.
        """
        path = []
        current = self
        while current.move is not None:
            path.append(current.move)
            current = current.parent  # type: ignore
        return list(reversed(path))

    def get_state_sequence(self) -> List['State']:
        """
        Reconstruct the sequence of states from initial to this state.

        Returns:
            List of State objects.
        """
        states = []
        current = self
        while current is not None:
            states.append(current)
            current = current.parent
        return list(reversed(states))

    def to_grid(self) -> List[List[int]]:
        """Convert flat board to 3x3 grid."""
        return [list(self.board[i * 3:(i + 1) * 3]) for i in range(3)]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, State):
            return False
        return self.board == other.board

    def __hash__(self) -> int:
        return hash(self.board)

    def __lt__(self, other: 'State') -> bool:
        """For priority queue ordering."""
        return self.cost < other.cost

    def __repr__(self) -> str:
        grid = self.to_grid()
        rows = [' '.join(str(x) if x != 0 else '_' for x in row) for row in grid]
        return '\n'.join(rows)
