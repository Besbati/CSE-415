"""EightPuzzleWithManhattan.py
This file augments EightPuzzle.py with heuristic information,
so that it can be used by an A* implementation.
The particular heuristic is the Manhattan Distance (sum of horizontal and vertical distances from the expected position)
"""

from EightPuzzle import *

LONGITUDE = {'Avignon': 48, 'Bordeaux': -6, 'Brest': -45, 'Caen': -4,
             'Calais': 18, 'Dijon': 51, 'Grenoble': 57, 'Limoges': 12,
             'Lyon': 48, 'Marseille': 53, 'Montpellier': 36, 'Nancy': 62,
             'Nantes': -16, 'Nice': 73, 'Paris': 23, 'Rennes': -17,
             'Strasbourg': 77, 'Toulouse': 14}


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