'''
charlez_KInARow.py
Authors: Hamilton-Eppler, Charles

An agent for playing "K-in-a-Row with Forbidden Squares" and related games.
CSE 473, University of Washington
'''

from random import randint
from agent_base import KAgent
from game_types import State, Game_Type
from charlez.charlez_staticEvals import expensive_staticEval, cheap_staticEval
from charlez.charlez_staticEvals import x_wins, o_wins

AUTHORS = 'Charles Hamilton-Eppler'

MAX_INT: int = 4294967296
TREE_DEPTH: int = 2

# Create your own type of agent by subclassing KAgent:


class OurAgent(KAgent):  # Keep the class name "OurAgent" so a game master
    # knows how to instantiate your agent class.

    def __init__(self, twin=False):
        self.twin=twin
        self.nickname = 'Strangler'
        if twin:
            self.nickname += ' Victim'
        self.long_name = 'Tattletale Strangler'
        if twin:
            self.long_name += ' II'
        self.persona = 'edgy and violent'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "don't know yet"  # e.g., "X" or "O".
        self.image = "./charlez/charlez-Strangler.jpg"

        """Below are additional fields for dealing with game state."""
        # Have to be introduced by prepare()
        self.game_type: Game_Type = None
        # Will be changed by prepare()
        self.opponent_nick: str = "Tattletale"
        # True by default.
        self.utterances_matter: bool = True
        self.zTable_nums: [[[int]]] = []
        # May change. Right now it's a dictionary of states' hash values.
        self.zTable: dict[int, float] = {}

        """Statistics for just our last move."""
        # Number of successful Zobrist lookups.
        self.recent_zHash_lookups: int = 0
        # Number of staticEval function CALLS.
        self.recent_static_eval_calls: int = 0
        # Number of staticEval COMPUTATIONS (unsuccessful Zobrist lookups).
        self.recent_static_eval_computations: int = 0
        # Number of branches pruned.
        self.recent_branches_pruned: int = 0

        """Fields to track statistics across the entire game"""
        # Total successful Zobrist lookups.
        self.zHash_lookups: int = 0
        # Total staticEval function CALLS.
        self.static_eval_calls: int = 0
        # Total staticEval COMPUTATIONS of static eval COMPUTATIONS.
        self.static_eval_computations: int = 0
        # Total branches bruned.
        self.branches_pruned: int = 0

    def introduce(self):
        intro = '\nMy name is the Tattletale Strangler.\n'+\
            'Charles made me (before I STRANGLED him).\n'+\
            'I\'m a violent criminal who strangles anyone who turns me in.\n'
        if self.twin:
            intro += 'Please!! I had to say that or else he\'d kill me!.\n'+\
                'I\'VE BEEN SET UP TO TAKE THE FALL!!'
        return intro

    # Receive and acknowledge information about the game from
    # the game master:
    def prepare(
        self,
        game_type,
        what_side_to_play,
        opponent_nickname,
        expected_time_per_move = 0.1, # Time limits can be
                                      # changed mid-game by the game master.
        utterances_matter=True):      # If False, just return 'OK' for each utterance.

        # Write code to save the relevant information in variables
        # local to this instance of the agent.
        # Game-type info can be in global variables.
        self.game_type = game_type
        self.playing = what_side_to_play
        self.opponent_nick = opponent_nickname
        self.utterances_matter = utterances_matter
        # And now some work to prepare the Zobrist hash table.
        # Current format is zTable_nums[i][j][marker].
        # Marker is 1 for X and zero for O.
        height: int = self.game_type.n
        width: int = self.game_type.m
        self.zTable_nums = [[[0, 0] for i in range(width)] for k in range(height)]
        for i in range(height):
            for j in range(width):
                self.zTable_nums[i][j][0] = randint(0, MAX_INT)
                self.zTable_nums[i][j][1] = randint(0, MAX_INT)
        return "OK"

    # The core of your agent's ability should be implemented here:             
    def makeMove(self, currentState, currentRemark, timeLimit=10000):
        # Reset the recent statistics.
        self.recent_static_eval_calls = 0
        self.recent_zHash_lookups = 0
        self.recent_static_eval_computations = 0
        self.recent_branches_pruned = 0

        assert (TREE_DEPTH > 0)
        [succ, move, score] = self.minimax(currentState,
                                           TREE_DEPTH,
                                           will_use_zHashing=True)
        if (succ is None) or (move is None) or (score is None):
            raise Exception("Agent did not find a proper move.")
        newRemark: str = self._utterance(score, currentRemark)
        return [[list(move), succ], newRemark]

    # The main adversarial search function:
    def minimax(self,
                state,
                depthRemaining,
                pruning=False,
                alpha=None,
                beta=None,
                zHashing=None,
                # True iff this minimax will use Zobrist hashing on the states.
                will_use_zHashing=False):
        # I'll call my helper methods to deal with the logic.
        if self.playing.lower() == 'x':
            result: (State, (int, int), int)\
                = self._maxiprune(state,
                                  depthRemaining,
                                  float('-inf'),
                                  float('+inf'),
                                  will_use_zHashing)
            return result
        elif self.playing.lower() == 'o':
            result: (State, (int, int), int)\
                = self._miniprune(state,
                                  depthRemaining,
                                  float('-inf'),
                                  float('+inf'),
                                  will_use_zHashing)
            return result
        else:
            raise Exception("Agent does not know who they're playing as!")

    # I went with the first static eval described in WE-2!
    def staticEval(self, state, zHashing: bool=True) -> float:
        # Always increment this by 1.
        self.static_eval_calls += 1
        self.recent_static_eval_calls += 1
        if zHashing:
            hash_val: int = self._zHash(state)
            # If it already exists in our Zobrist hash table, just return it!
            # Yes, this currently implementation doesn't resolve collisions.
            if hash_val in self.zTable:
                # A (presumably) successful zTable lookup!
                self.zHash_lookups += 1
                self.recent_zHash_lookups += 1
                return self.zTable.get(hash_val)

        # Not in our zTable? We have to do a computation.
        self.static_eval_computations += 1
        self.recent_static_eval_computations += 1
        val: float
        # As it turns out, I created two static evaluation functions.
        # As such, I can give the old one to my twin!
        if self.twin:
            val = cheap_staticEval(state)
        else:
            val = expensive_staticEval(state, self.game_type.k)
        # If using Zobrist hashing, insert the hashcode and value.
        if zHashing:
            hash_val: int = self._zHash(state)
            self.zTable[hash_val] = val
        return val



    """
    Below are helper functions I've written for choosing a move to make.
    """

    # Each call to maxiprune or miniprune returns an action, value pair.
    # This allows minimizers and maximizers to associate actions with values.
    def _maxiprune(self,
                   state: State,
                   depthRemaining: int,
                   alpha: float,
                   beta: float,
                   zHashing: bool) -> (State, (int, int), float):
        # If we're out of depth, we statically evaluate.
        # If it's already a won or lost game, we can just return any move.
        if depthRemaining <= 0:
            return (None, None, self.staticEval(state, zHashing))
        states_and_moves: [(State, (int, int))] = self._successors_and_moves(state)
        # Check if the game is over.
        if len(states_and_moves) <= 0:
            return (None, None, self.staticEval(state, zHashing))
        elif o_wins(state, self.game_type.k):
            return (states_and_moves[0][0], states_and_moves[0][1], float('-inf'))
        elif x_wins(state, self.game_type.k):
            return (states_and_moves[0][0], states_and_moves[0][1], float('+inf'))
        # Making v initially an infinite value WOULD be cleaner.
        # But that clobbers comparisons if every successor state is also infinite.
        best_succ, best_move, v = (None, None, None)
        branches_evaluated: int = 0
        for succ, move in states_and_moves:
            branches_evaluated += 1
            v1: float = self._miniprune(succ, depthRemaining - 1, alpha, beta, zHashing)[2]
            # Did this action yield a greater result? If so, update!
            if v is None or v1 > v:
                v = v1
                best_move = move
                best_succ = succ
            if v > beta:
                # This is how many branches we WON'T have to evaluate.
                self.branches_pruned += len(states_and_moves) - branches_evaluated
                self.recent_branches_pruned += len(states_and_moves) - branches_evaluated
                return (best_succ, best_move, v)
            alpha = max(v, alpha)
        return (best_succ, best_move, v)


    # Each call to maxiprune or miniprune returns an action, value pair.
    # This allows minimizers and maximizers to associate actions with values.
    def _miniprune(self,
                   state: State,
                   depthRemaining: int,
                   alpha: float,
                   beta: float,
                   zHashing: bool) -> (State, (int, int), float):
        # If we're out of depth, we statically evaluate.
        if depthRemaining <= 0:
            return (None, None, self.staticEval(state, zHashing))
        states_and_moves: [(State, (int, int))] = self._successors_and_moves(state)
        # Check if the game is over.
        # If it's already a won or lost game, we can just return any move.
        if len(states_and_moves) <= 0:
            return (None, None, self.staticEval(state, zHashing))
        elif o_wins(state, self.game_type.k):
            return (states_and_moves[0][0], states_and_moves[0][1], float('-inf'))
        elif x_wins(state, self.game_type.k):
            return (states_and_moves[0][0], states_and_moves[0][1], float('+inf'))
        # Making v initially an infinite value WOULD be cleaner.
        # But that clobbers comparisons if every successor state is also infinite.
        best_succ, best_move, v = (None, None, None)
        branches_evaluated: int = 0
        for succ, move in states_and_moves:
            branches_evaluated += 1
            v1: float = self._maxiprune(succ, depthRemaining - 1, alpha, beta, zHashing)[2]
            # Did this action yield a smaller result? If so, update!
            if v is None or v1 < v:
                v = v1
                best_move = move
                best_succ = succ
            if v < alpha:
                # This is how many branches we WON'T have to evaluate.
                self.branches_pruned += len(states_and_moves) - branches_evaluated
                self.recent_branches_pruned += len(states_and_moves) - branches_evaluated
                return (best_succ, best_move, v)
            beta = min(v, beta)
        return (best_succ, best_move, v)

    # Computes the Zobrist hash code of a state.
    def _zHash(self, state: State) -> int:
        val: int = 0
        height: int = self.game_type.n
        width: int = self.game_type.m
        for i in range(height):
            for j in range(width):
                marker: str = state.board[i][j]
                if marker.lower() == 'o':
                    val ^= self.zTable_nums[i][j][0]
                elif marker.lower() == 'x':
                    val ^= self.zTable_nums[i][j][1]
        return val

    # Sorry! I felt like borrowing this (but modifying it)
    # Returns a list of tuples. Each tuple is a state and an int pair (a move)
    def _successors_and_moves(self, state: State) -> [(State, (int, int))]:
        board: [[str]] = state.board
        states_and_moves: [(State, (int, int))] = []
        height: int = len(board)
        length: int = len(board[0])

        for i in range(height):
            for j in range(length):
                if board[i][j] == ' ':
                    # Build a new state using the old state and current move.
                    succ: State = State(old=state)
                    succ.board[i][j] = state.whose_move
                    succ.change_turn()
                    states_and_moves.append((succ, (i, j)))
        return states_and_moves


    """
    Below are helper functions to determine what utterances to say.
    """

    def _utterance(self, score: float, prevRemark: str) -> str:
        # If asked something about the previous move or the game so far.
        prev: str = prevRemark.lower()
        if prev == "tell me how you did that" or prev == "tell me how you did that.":
            return self._about_move()
        elif (prev == "what's your take on the game so far?")\
                or (prev == "what's your take on the game so far"):
            return self._about_game()
        # If on the fringe of winning or losing.
        if (score == float('+inf') and self.playing.lower() == 'x') \
                or (score == float('-inf') and self.playing.lower() == 'o'):
            return "MUAHAHAHAHA! NOW YOU'RE GONNA GET YOURS!!"
        elif (score == float('+inf') and self.playing.lower() == 'o') \
                or (score == float('-inf') and self.playing.lower() == 'x'):
            return "HOW COULD YOU POSSIBLY BE ON YOUR WAY TO WIN?!" \
                + " IS THERE A TATTLETALE TELLING YOU MY STRATEGY?!"
        # Small chance to ask about the previous move or game so far.
        randy: int = randint(1, 20)
        if randy == 1:
            return "Tell me how you did that"
        elif randy == 2:
            return "What's your take on the game so far?"
        # General utterances about who's winning the game.
        # First branch means agent is at an advantage (but not fully winning).
        # Second branch means agent is at a disadvantage (but not doomed).
        # Third branch means both agents are dead even in terms of score.
        if (score > 0 and self.playing.lower() == 'x') \
                or (score < 0 and self.playing.lower() == 'o'):
            return self._positive_utterance()
        elif (score > 0 and self.playing.lower() == 'o') \
                or (score < 0 and self.playing.lower() == 'x'):
            return self._negative_utterance()
        else:
            return "Wait we're evenly matched?!" if randint(1, 2) == 1\
                else "How are we still evenly matched?!"

    # Uttered if agent is at an advantage.
    def _negative_utterance(self) -> str:
        randy: int = randint(1, 8)
        if randy == 1:
            return "Get away from me, you maniac!"
        elif randy == 2:
            return "BEWARE!! My vengeance will be swift and merciless!"
        elif randy == 3:
            return "ENOUGH!! LET'S TAKE THIS OUTSIDE!"
        elif randy == 4:
            return "In case you hadn't noticed, you may be winning, but don't get cocky."
        elif randy == 5:
            return "HOW DID YOU FIND THAT MOVE??"
        elif randy == 6:
            return "NOO!!!"
        elif randy == 7:
            return "*Ugh...* Too many witnesses."
        else:
            return "Perhaps we should finish this game someplace quiet, "\
                + "like in a dark alley or behind a dumpster, or..."

    # Uttered if agent is at a disadvantage.
    def _positive_utterance(self) -> str:
        randy: int = randint(1, 6)
        if randy == 1:
            return "Heh... you don't look so tough!"
        elif randy == 2:
            return "I can take anything you throw at me! I'm actually going to win!"
        elif randy == 3:
            return "Yeah I'm winning. What are you gonna do about it?!"
        elif randy == 4:
            return "I strangled the last person who tried to turn me in and you're next!!"
        elif randy == 5:
            return "So we're all alone... FINALLY!"
        else:
            return "YOU IDIOT!! YOU DON'T STAND A CHANCE!"

    # Uttered if opponent asked about the game overall.
    def _about_game(self) -> str:
        return "I've crushed the windpipe of " + str(self.branches_pruned)\
            + " branches! I've had to call " + str(self.static_eval_calls)\
            + " static evals, but I escaped " + str(self.zHash_lookups)\
            + " of them using Zobrist lookups!"

    # Uttered if opponent asked about the previous move.
    def _about_move(self) -> str:
        return "This move alone I've strangled " + str(self.branches_pruned)\
            + " branches! I've had to call " + str(self.static_eval_calls)\
            + " static evals, but I escaped " + str(self.zHash_lookups)\
            + " of them using Zobrist lookups!"



# OPTIONAL THINGS TO KEEP TRACK OF:

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances

