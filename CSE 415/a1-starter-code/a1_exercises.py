# Starter code file for A1.  Remove this line before submission to Gradescope.
# Lucas Besbati besbati
# CSE 415, Assignment 1, Winter 2025.
import math


def is_a_quintuple(n):
    """Return True if n is a multiple of 5; False otherwise."""
    return n % 5 == 0


def is_prime(m):
    if m <= 1:
        return False
    if m == 2:
        return True
    if m % 2 == 0:
        return False

    for i in range(3, int(math.sqrt(m)) + 1, 2):
        if m % i == 0:
            return False
    return True


def last_prime(m):
    """Return the largest prime number p that is less than or equal to m.
    You might wish to define a helper function for this.
    You may assume m is a positive integer."""
    if m < 2:
        return None
    for i in range(m, 1, -1):
        if is_prime(i):
            return i


def quadratic_roots(a, b, c):
    """Return the roots of a quadratic equation (real cases only).
    Return results in tuple-of-floats form, e.g., (-7.0, 3.0)
    Return "complex" if real roots do not exist."""
    under_root = b ** 2 - 4 * a * c
    if under_root < 0:
        return "complex"
    squared_root = math.sqrt(under_root)
    plus = (-b + squared_root) / 2 * a
    minus = (-b - squared_root) / 2 * a
    return (plus, minus)


def new_quadratic_function(a, b, c):
    """Create and return a new, anonymous function (for example
    using a lambda expression) that takes one argument x and 
    returns the value of ax^2 + bx + c."""
    return lambda x: a * x ** 2 + b * x + c


def perfect_shuffle(even_list):
    """Assume even_list is a list of an even number of elements.
    Return a new list that is the perfect-shuffle of the input.
    Perfect shuffle means splitting a list into two halves and then interleaving
    them. For example, the perfect shuffle of [0, 1, 2, 3, 4, 5, 6, 7] is
    [0, 4, 1, 5, 2, 6, 3, 7]."""
    i = 0
    res = []
    for j in range(len(even_list) // 2, len(even_list)):
        res.append(even_list[i])
        res.append(even_list[j])
        i += 1
    return res


def list_of_5_times_elts_plus_1(input_list):
    """Assume a list of numbers is input. Using a list comprehension,
    return a new list in which each input element has been multiplied
    by 5 and had 1 added to it."""
    return [((num * 5) + 1) for num in input_list]


def double_vowels(text):
    """Return a new version of text, with all the vowels doubled.
    For example:  "The *BIG BAD* wolf!" => "Theee "BIIG BAAD* woolf!".
    For this exercise assume the vowels are
    the characters A,E,I,O, and U (and a,e,i,o, and u).
    Maintain the case of the characters."""
    vowels_set = {'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'}
    res = ""
    for i in range(len(text)):
        if text[i] in vowels_set:
            res += text[i]
        res += text[i]
    return res


def count_words(text):
    """Return a dictionary having the words in the text as keys,
    and the numbers of occurrences of the words as values.
    Assume a word is a substring of letters and digits and the characters
    '-', '+', *', '/', '@', '#', '%', and "'" separated by whitespace,
    newlines, and/or punctuation (characters like . , ; ! ? & ( ) [ ] { } | : ).
    Convert all the letters to lower-case before the counting."""
    text = text.lower()
    allowed = set("1234567890abcdefghijklmnopqrstuvwxyz-+*/@#%'")
    cleaned = []

    for c in text:
        if c in allowed:
            cleaned.append(c)
        else:
            cleaned.append(" ")
    cleaned_text = "".join(cleaned)

    words = cleaned_text.split()
    res = {}
    for w in words:
        res[w] = res.get(w, 0) + 1

    return res


class TTT_State:

    def __init__(self):
        '''Create an instance. This happens to represent the initial state
        for Tic-Tac-Toe.'''
        self.board = [[" ", " ", " "],
                      [" ", " ", " "],
                      [" ", " ", " "]]
        self.whose_move = 'X'

    def __str__(self):
        '''Return a string representation of the
        state that show the Tic-Tac-Toe board as a 2-D ASCII display.
        Style it simply, as you wish.'''
        rows = []
        for row in self.board:
            rows.append(" | ".join(row))
        return "\n---------\n".join(rows)

    def __deepcopy__(self):
        '''Return a new instance with the same board arrangement 
        and player to move. 
        (Sublists must be copies, not copies of references.)'''
        game_copy = TTT_State()

        game_copy.board = [row[:] for row in self.board]

        game_copy.whose_move = self.whose_move

        return game_copy

    def __eq__(self, other):
        '''Return True iff two states are equal.'''
        # check if other is indeed an instance
        if not isinstance(other, TTT_State):
            return False
        return self.board == other.board and self.whose_move == other.whose_move


class TTT_Operator:
    '''An instance of this class will represent an
    operator that can make a move by who (either 'X' or 'O'),
    to the given row and column. '''

    def __init__(self, who, row, col):
        self.who = who
        self.row = row
        self.col = col

    def is_applicable(self, state):
        '''Return True iff it would be legal to apply
        this operator to the given state.'''
        if state.whose_move != self.who:
            return False
        if state.board[self.row][self.col] != " ":
            return False
        return True

    def apply(self, state):
        '''Return a new state object that represents the
        result of applying this operator to the given state.'''
        if not self.is_applicable(state):
            raise ValueError("Illegal Move")

        new_state = state.__deepcopy__()

        new_state.board[self.row][self.col] = self.who

        if new_state.whose_move == 'X':
            new_state.whose_move = 'O'
        else:
            new_state.whose_move = 'X'

        return new_state
