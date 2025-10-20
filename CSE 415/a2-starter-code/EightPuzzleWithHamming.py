"""EightPuzzleWithHamming.py
This file augments EightPuzzle.py with heuristic information,
so that it can be used by an A* implementation.
The particular heuristic is the Hamming Distance (number of tiles out of place, excluding the blank)

"""

from EightPuzzle import *

LONGITUDE = {'Avignon': 48, 'Bordeaux': -6, 'Brest': -45, 'Caen': -4,
             'Calais': 18, 'Dijon': 51, 'Grenoble': 57, 'Limoges': 12,
             'Lyon': 48, 'Marseille': 53, 'Montpellier': 36, 'Nancy': 62,
             'Nantes': -16, 'Nice': 73, 'Paris': 23, 'Rennes': -17,
             'Strasbourg': 77, 'Toulouse': 14}


def h(s):
    """We return the number of out of place tiles in s."""
    hamming_distance = 0
    for i in range(3):
        for j in range(3):
            if s.b[i][j] != (i * 3) + j and s.b[i][j] != 0: hamming_distance += 1
    return hamming_distance