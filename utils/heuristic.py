from __future__ import annotations
from typing import Tuple, Dict


GOAL_POSITIONS: Dict[int, Tuple[int, int]] = {
    1: (0, 0), 2: (0, 1), 3: (0, 2),
    4: (1, 0), 5: (1, 1), 6: (1, 2),
    7: (2, 0), 8: (2, 1), 0: (2, 2),
}


def misplaced_tiles(board: Tuple[int, ...], goal: Tuple[int, ...] = (1,2,3,4,5,6,7,8,0)) -> int:
    """
    Count the number of tiles not in their goal position.
    Blank tile (0) is not counted.

    Args:
        board: Current board configuration.
        goal: Goal board configuration.

    Returns:
        Number of misplaced tiles.
    """
    return sum(1 for i, tile in enumerate(board) if tile != 0 and tile != goal[i])


def manhattan_distance(board: Tuple[int, ...], goal: Tuple[int, ...] = (1,2,3,4,5,6,7,8,0)) -> int:
    """
    Sum of Manhattan distances of each tile from its goal position.
    Blank tile (0) is not counted.

    Args:
        board: Current board configuration.
        goal: Goal board configuration.

    Returns:
        Total Manhattan distance.
    """
    # Build goal position map from goal tuple
    goal_pos: Dict[int, Tuple[int, int]] = {}
    for idx, tile in enumerate(goal):
        goal_pos[tile] = divmod(idx, 3)

    total = 0
    for idx, tile in enumerate(board):
        if tile == 0:
            continue
        row, col = divmod(idx, 3)
        gr, gc = goal_pos[tile]
        total += abs(row - gr) + abs(col - gc)
    return total


def linear_conflict(board: Tuple[int, ...], goal: Tuple[int, ...] = (1,2,3,4,5,6,7,8,0)) -> int:
    """
    Manhattan distance + 2 * number of linear conflicts.
    A linear conflict occurs when two tiles are in their goal row/col
    but in wrong order.

    Args:
        board: Current board configuration.
        goal: Goal board configuration.

    Returns:
        Linear conflict heuristic value.
    """
    goal_pos: Dict[int, Tuple[int, int]] = {}
    for idx, tile in enumerate(goal):
        goal_pos[tile] = divmod(idx, 3)

    md = manhattan_distance(board, goal)
    conflicts = 0

    # Check rows
    for row in range(3):
        row_tiles = []
        for col in range(3):
            tile = board[row * 3 + col]
            if tile != 0 and goal_pos[tile][0] == row:
                row_tiles.append((tile, col, goal_pos[tile][1]))

        for i in range(len(row_tiles)):
            for j in range(i + 1, len(row_tiles)):
                ti, ci, gi = row_tiles[i]
                tj, cj, gj = row_tiles[j]
                if ci < cj and gi > gj:
                    conflicts += 1
                elif ci > cj and gi < gj:
                    conflicts += 1

    # Check columns
    for col in range(3):
        col_tiles = []
        for row in range(3):
            tile = board[row * 3 + col]
            if tile != 0 and goal_pos[tile][1] == col:
                col_tiles.append((tile, row, goal_pos[tile][0]))

        for i in range(len(col_tiles)):
            for j in range(i + 1, len(col_tiles)):
                ti, ri, gi = col_tiles[i]
                tj, rj, gj = col_tiles[j]
                if ri < rj and gi > gj:
                    conflicts += 1
                elif ri > rj and gi < gj:
                    conflicts += 1

    return md + 2 * conflicts


# Registry of available heuristics
HEURISTICS: Dict[str, callable] = {
    "Misplaced Tiles": misplaced_tiles,
    "Manhattan Distance": manhattan_distance,
    "Linear Conflict": linear_conflict,
}
