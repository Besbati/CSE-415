"""EightPuzzleWithManhattan.py
This file augments EightPuzzle.py with heuristic information,
so that it can be used by an A* implementation.
The particular heuristic is the Manhattan Distance (sum of horizontal and vertical distances from the expected position)
"""

from EightPuzzle import *

def h(s):
    """We return the Manhattan distance of each tile from its goal position in s."""
    manhattan_distance = 0
    for i in range(3):
        for j in range(3):
            tile = s.b[i][j]
            if tile != (i * 3) + j and tile != 0:
                row_difference = abs((tile // 3) - i)
                col_difference = abs((tile % 3) - j)
                manhattan_distance += row_difference + col_difference
    return manhattan_distance