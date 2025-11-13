from game_types import State


"""
A reasonably cheap static evaluation function.
I initially used this one, but I've since written a stronger eval function.
"""


# The FIRST static eval function described in WE-2.
def cheap_staticEval(state: State) -> float:
    val: int = 0
    height: int = len(state.board)
    width: int = len(state.board[0])
    for i in range(height):
        for j in range(width):
            marker: str = state.board[i][j]
            # If X, add +1 for all adjacent empty spots.
            # If O, subtract 1 for all adjacent empty spots.
            if marker.lower() == 'x':
                val += addAdjacents(state, (i, j))
            elif marker.lower() == 'o':
                val -= addAdjacents(state, (i, j))
    return val


# Add +1 for all empty spots adjacent to pos.
def addAdjacents(state: State, pos: (int, int)):
    height: int = len(state.board)
    width: int = len(state.board[0])
    res: int = 0
    i, j = pos
    board: [[str]] = state.board
    if i > 0 and j > 0 and board[i - 1][j - 1] == ' ':
        res += 1
    if j > 0 and board[i][j - 1] == ' ':
        res += 1
    if i < height - 1 and j > 0 and board[i + 1][j - 1] == ' ':
        res += 1
    if i < height - 1 and board[i + 1][j] == ' ':
        res += 1
    if i < height - 1 and j < width - 1 and board[i + 1][j + 1] == ' ':
        res += 1
    if j < width - 1 and board[i][j + 1] == ' ':
        res += 1
    if i > 0 and j < width - 1 and board[i - 1][j + 1] == ' ':
        res += 1
    if i > 0 and board[i - 1][j] == ' ':
        res += 1
    return res


"""
A VERY EXPENSIVE static evaluation function.
"""


# This attempts to compute the SECOND static eval function described in WE-2.
# Unlike the first, this is a VERY involved computation.
def expensive_staticEval(state: State, k: int) -> float:
    score: int = 0
    for n in range(1, k + 1):
        this_iteration: int = 0
        this_iteration += unblocked_rows(state, k, n, 'X')
        this_iteration -= unblocked_rows(state, k, n, 'O')
        this_iteration += unblocked_columns(state, k, n, 'X')
        this_iteration -= unblocked_columns(state, k, n, 'O')
        this_iteration += unblocked_diagonals(state, k, n, 'X')
        this_iteration -= unblocked_diagonals(state, k, n, 'O')
        this_iteration += unblocked_lanogaids(state, k, n, 'X')
        this_iteration -= unblocked_lanogaids(state, k, n, 'O')
        # If we've found unblocked rows of length less than k:
        # * Raise their net total to the power of n.
        # If we've found unblocked rows of length k:
        # * Return negative infinity if negative, positive infinity if positive.
        if n < k:
            score += this_iteration * (10 ** n)
        elif this_iteration < 0:
            return float('-inf')
        elif this_iteration > 0:
            return float('+inf')
    return score


# How many unblocked COLUMNS are there of length n?
# An unblocked lane of length n means:
# * It has n consecutive instances of the marker.
# * It's padded to length k SOLELY by blank spaces.
def unblocked_rows(state: State, k: int, n: int, marker: str) -> int:
    height: int = len(state.board)
    width: int = len(state.board[0])
    unblocked_n_rows: int = 0
    # Find the unblocked rows of length n for the specified marker.
    for i in range(height):
        # How long this row is currently unblocked for.
        lane: int = 0
        # How many of our marker we've seen consecutively.
        seen: int = 0
        # How many times have we last seen our marker (or any non-empty space)?
        gap: int = 0
        for j in range(width):
            icon: str = state.board[i][j]
            lane, seen, gap = lane_logic(icon, marker, lane, seen, gap, n)
            # Have we seen n markers in a row
            # AND is said row padded to five spaces?
            if seen == n and lane == k:
                unblocked_n_rows += 1
                break
    return unblocked_n_rows


# How many unblocked COLUMNS are there of length n?
# An unblocked lane of length n means:
# * It has n consecutive instances of the marker.
# * It's padded to length k SOLELY by blank spaces.
def unblocked_columns(state: State, k: int, n: int, marker: str) -> int:
    height: int = len(state.board)
    width: int = len(state.board[0])
    unblocked_n_columns: int = 0
    # Find the unblocked rows of length n for the specified marker.
    for j in range(width):
        # How long this row is currently unblocked for.
        lane: int = 0
        # How many of our marker we've seen consecutively.
        seen: int = 0
        # How many times have we last seen our marker (or any non-empty space)?
        gap: int = 0
        for i in range(height):
            icon: str = state.board[i][j]
            lane, seen, gap = lane_logic(icon, marker, lane, seen, gap, n)
            # Have we seen n markers in a row
            # AND is said row padded to five spaces?
            if seen == n and lane == k:
                unblocked_n_columns += 1
                break
    return unblocked_n_columns


# How many unblocked UPWARD DIAGONALS are there of length n?
#                     /
#  Upward Diagonal:  /
#                   /
# An unblocked lane of length n means:
# * It has n consecutive instances of the marker.
# * It's padded to length k SOLELY by blank spaces.
def unblocked_diagonals(state: State, k: int, n: int, marker: str) -> int:
    height: int = len(state.board)
    width: int = len(state.board[0])
    unblocked_n_diagonals: int = 0
    for y in range(height):
        i, j = y, 0
        # How long this row is currently unblocked for.
        lane: int = 0
        # How many of our marker we've seen consecutively.
        seen: int = 0
        # How many times have we last seen our marker (or any non-empty space)?
        gap: int = 0
        while i < height and j < width:
            icon: str = state.board[i][j]
            lane, seen, gap = lane_logic(icon, marker, lane, seen, gap, n)
            # Have we seen n markers in a row
            # AND is said row padded to five spaces?
            if seen == n and lane == k:
                unblocked_n_diagonals += 1
                break
            i -= 1
            j += 1

    for x in range(1, width):
        i, j = height - 1, x
        # How long this row is currently unblocked for.
        lane: int = 0
        # How many of our marker we've seen consecutively.
        seen: int = 0
        # How many times have we last seen our marker (or any non-empty space)?
        gap: int = 0
        while i < height and j < width:
            icon: str = state.board[i][j]
            lane, seen, gap = lane_logic(icon, marker, lane, seen, gap, n)
            # Have we seen n markers in a row
            # AND is said row padded to five spaces?
            if seen == n and lane == k:
                unblocked_n_diagonals += 1
                break
            i -= 1
            j += 1
    return unblocked_n_diagonals


# How many unblocked DOWNWARD DIAGONALS are there of length n?
#                     \
#  Downward Diagonal:  \
#                       \
# An unblocked lane of length n means:
# * It has n consecutive instances of the marker.
# * It's padded to length k SOLELY by blank spaces.
def unblocked_lanogaids(state: State, k: int, n: int, marker: str) -> int:
    height: int = len(state.board)
    width: int = len(state.board[0])
    unblocked_n_lanogaids: int = 0
    for y in range(height):
        i, j = y, 0
        # How long this row is currently unblocked for.
        lane: int = 0
        # How many of our marker we've seen consecutively.
        seen: int = 0
        # How many times have we last seen our marker (or any non-empty space)?
        gap: int = 0
        while i < height and j < width:
            icon: str = state.board[i][j]
            lane, seen, gap = lane_logic(icon, marker, lane, seen, gap, n)
            # Have we seen n markers in a row
            # AND is said row padded to five spaces?
            if seen == n and lane == k:
                unblocked_n_lanogaids += 1
                break
            i += 1
            j += 1

    for x in range(1, width):
        i, j = 0, x
        # How long this row is currently unblocked for.
        lane: int = 0
        # How many of our marker we've seen consecutively.
        seen: int = 0
        # How many times have we last seen our marker (or any non-empty space)?
        gap: int = 0
        while i < height and j < width:
            icon: str = state.board[i][j]
            lane, seen, gap = lane_logic(icon, marker, lane, seen, gap, n)
            # Have we seen n markers in a row
            # AND is said row padded to five spaces?
            if seen == n and lane == k:
                unblocked_n_lanogaids += 1
                break
            i += 1
            j += 1
    return unblocked_n_lanogaids


# Logic to determine if the lane is unblocked or blocked.
# Parameters:
# * Icon: The icon on the board we're examining.
# * Marker:
# * Lane: How long the lane is unblocked for.
# * Seen: How many of that marker we've seen in a row.
# * Gap: How long since we've last seen a non-empty space.
def lane_logic(icon: str,
               marker: str,
               lane: int,
               seen: int,
               gap: int,
               n: int) -> (int, int, int):
    if icon == ' ':
        lane += 1
        gap += 1
    elif icon == marker and seen == n:
        lane = seen
    elif icon == marker and gap > 0:
        lane = gap + 1
        seen = 1
        gap = 0
    elif icon == marker:
        lane += 1
        seen += 1
    else:
        lane = 0
        seen = 0
        gap = 0
    return (lane, seen, gap)


"""
The next two functions determine if the state is a win for X or O.
They use parts of the expensive static eval function defined above.
"""


# True iff the board is a win for X. False if lost or game still going.
def x_wins(state: State, k: int) -> bool:
    if unblocked_rows(state, k, k, 'X') > 0:
        return True
    elif unblocked_columns(state, k, k, 'X') > 0:
        return True
    elif unblocked_diagonals(state, k, k, 'X') > 0:
        return True
    elif unblocked_lanogaids(state, k, k, 'X') > 0:
        return True
    return False


# True iff the board is a win for O. False if won or game still going.
def o_wins(state: State, k: int) -> bool:
    if unblocked_rows(state, k, k, 'O') > 0:
        return True
    elif unblocked_columns(state, k, k, 'O') > 0:
        return True
    elif unblocked_diagonals(state, k, k, 'O') > 0:
        return True
    elif unblocked_lanogaids(state, k, k, 'O') > 0:
        return True
    return False
