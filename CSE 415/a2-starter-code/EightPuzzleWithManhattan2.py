"""EightPuzzleWithManhattan2.py
This file augments EightPuzzle.py with heuristic information,
so that it can be used by an A* implementation.
The particular heuristic is a modification of the Manhattan Distance (sum of horizontal and vertical distances from the expected position)
The heuristic adds 1 IF there is already something in that position that a displaced tile needs to be in (as it requires moving that to move to the tile there)
This heuristic is inadmissible, but helped in finding the last one. It also sometimes works better than the Manhattan distance (but sometimes worse)
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
                if s.b[expected_row][expected_col] != 0:
                    manhattan_distance += 1
    return manhattan_distance