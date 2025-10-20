"""EightPuzzleWithManhattan3.py
This file augments EightPuzzle.py with heuristic information,
so that it can be used by an A* implementation.
The particular heuristic is a modification of the Manhattan Distance (sum of horizontal and vertical distances from the expected position)
The heuristic adds 2 for every pair that needs to swap positions but is in the same row or column.
"""

from EightPuzzle import *

def h(s):
    """We return the Manhattan distance of each tile from its goal position in s."""
    manhattan_distance = 0
    for i in range(3):
        for j in range(3):
            tile = s.b[i][j]
            if tile != (i * 3) + j and tile != 0:
                expected_row = tile // 3
                expected_col = tile % 3
                manhattan_distance += abs(expected_row - i) + abs(expected_col - j)
                current_tile = s.b[expected_row][expected_col]
                if current_tile // 3 == i and current_tile % 3 == j and (expected_row == i ^ expected_col == j):
                    manhattan_distance += 1 # this adds 1 for the first object in the pair and adds another for the second object in the pair
    return manhattan_distance