'''
flynger_KInARow.py
Authors: Singh, Arnav

An agent for playing "K-in-a-Row with Forbidden Squares" and related games.
CSE 473, University of Washington

THIS IS A TEMPLATE WITH STUBS FOR THE REQUIRED FUNCTIONS.
YOU CAN ADD WHATEVER ADDITIONAL FUNCTIONS YOU NEED IN ORDER
TO PROVIDE A GOOD STRUCTURE FOR YOUR IMPLEMENTATION.

'''

from agent_base import KAgent
from game_types import State, Game_Type
import game_types

AUTHORS = 'Arnav Singh'
PLAYER_TOKENS = { "X", "O" }
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (-1, 1)]

import time # You'll probably need this to avoid losing a
 # game due to exceeding a time limit.
import math
import random

# Create your own type of agent by subclassing KAgent:

class OurAgent(KAgent):  # Keep the class name "OurAgent" so a game master
    # knows how to instantiate your agent class.
    WINNING_UTTERANCES = {
        "default": [
            "Oh, you thought you had a chance? That's adorable.",
            "Is that the best you've got?",
            "To be honest, I expected more of a challenge.",
            "Another round? Just prolonging the inevitable, huh?",
            "I'm just getting warmed up.",
            "I'd say I'm sorry, but it's honestly not my fault you're this predictable.",
            "I bet you didn't see that coming."
        ],
        "twin": [
            "Efficient as always. Another clean victory.",
            "I told you, it's not about flash. Just results.",
            "Done already? Thought you'd last longer."
        ]
    }
    LOSING_UTTERANCES = {
        "default": [
            "I'm just letting you win. I'm tired of winning anyway.",
            "I'm just losing to try and make this interesting for you. You're welcome."
            "Well, at least I'm losing with style.",
            "I was saving my best moves for last.",
            "This is only happening because I'm testing out a new strategy, okay?",
            "You're... winning... How?"
        ],
        "twin": [
            "Not my best, but it won't happen again.",
            "You got this one. Don't expect it twice.",
            "A minor setback. I'll fix that next time."
        ]
    }
    EQUAL_UTTERANCES = {
        "default": [
            "I just prefer more neck-and-neck matches, that's all.",
            "Well, look at that. We're both equally mediocre.",
            "Well, well, look who's playing it safe.",
            "We're equal. How... unsatisfying.",
            "It's cute that you think you're winning. Spoiler: It's just a draw."
        ],
        "twin": [
            "Balanced, for now. But balance doesn't last.",
            "A draw? It's just delaying the inevitable.",
            "A tie. Let's break it next time."
        ]
    }

    def __init__(self, twin=False):
        self.twin=twin
        self.nickname = 'The Snark'
        if twin:
            self.nickname = 'Alex'
        self.long_name = 'Maxwell Sterling'
        if twin:
            self.long_name = 'Alex Sterling'
        self.persona = 'snarky'
        if twin:
            self.persona = 'efficient'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "don't know yet" # e.g., "X" or "O".

    def introduce(self):
        intro = "\nOh, you haven't heard of me? That's cute.\n"+\
            "Name's Max Sterling, but most people just call me 'The Snark.'\n"+\
            "I can't wait to see you get crushed. Makes it more fun. For me, at least.\n"+\
            'I was made by Arnav.\n'
        if self.twin:
            intro = "\nOh, so you've heard of my brother, Max?\n"+\
            "Max is all about the show, the flair. Me? I'm more about results.\n"+\
            "You can call me Alex Sterling, and unlike my brother, I don't need a nickname to prove a point.\n"+\
            'I was made by Arnav.\n'
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
       self.side = what_side_to_play
       self.opponent_nickname = opponent_nickname
       self.utterances_matter = utterances_matter

       m, n = self.game_type.m, self.game_type.n
       self.zobrist_nums = [[[random.randint(0, 2 ** 32), random.randint(0, 2 ** 32)] for x in range(m)] for y in range(n)]
       self._zobristTable = {}

       return "OK"
   
    # The core of your agent's ability should be implemented here:             
    def makeMove(self, currentState, currentRemark, timeLimit=10000):
        value, move, newState = self.minimax(currentState, 2, True, zHashing=True)
    
        if self.utterances_matter:
            newRemark = self._get_utterance(value, currentRemark)
        else:
            newRemark = "OK"

        return [[move, newState], newRemark]

    # The main adversarial search function:
    def minimax(self,
            state,
            depthRemaining,
            pruning=False,
            alpha=float('-inf'),
            beta=float('inf'),
            zHashing=None):
        succ_and_moves = self._successors_and_moves(state)

        if depthRemaining == 0 or not succ_and_moves:
            return [self.staticEval(state, zHashing), None, None]

        if state.whose_move != self.side:
            depthRemaining -= 1

        if state.whose_move == "X":
            compareFn = lambda a, b: a >= b
            alphaUpdate = max
            betaUpdate = lambda a, b: a  # No-op for beta in X's move
            bestValue = float('-inf')
        else:
            compareFn = lambda a, b: a <= b
            alphaUpdate = lambda a, b: a  # No-op for alpha in O's move
            betaUpdate = min
            bestValue = float('inf')

        bestMove = None
        bestSucc = None

        for move, succ in succ_and_moves:
            value, _, _ = self.minimax(succ, depthRemaining, pruning, alpha, beta, zHashing)
            if compareFn(value, bestValue):
                if pruning:
                    alpha = alphaUpdate(alpha, value)
                    beta = betaUpdate(beta, value)
                    if alpha > beta:
                        return value, move, succ
                bestValue = value
                bestMove = move
                bestSucc = succ

        return [bestValue, bestMove, bestSucc]
        # Only the score is required here but other stuff can be returned
        # in the list, after the score, in case you want to pass info
        # back from recursive calls that might be used in your utterances,
        # etc. 
 
    def staticEval(self, state, zHashing=None):
        # Values should be higher when the states are better for X,
        # lower when better for O.
        if zHashing:
            hash = self._zobristHash(state)
            if hash in self._zobristTable:
                return self._zobristTable.get(hash)
        score = 0
        board = state.board
        k, m, n = self.game_type.k, self.game_type.m, self.game_type.n

        for y in range(n):
            for x in range(m):
                if board[y][x] == "-":
                    continue

                for dx, dy in DIRECTIONS:
                    # Check sequences for X
                    count = self._check_line(board, m, n, k, x, y, dx, dy, "X")
                    if count == k:
                        return float('inf')
                    elif count >= 1:
                        score += 2 ** count

                    # Check sequences for O
                    count = self._check_line(board, m, n, k, x, y, dx, dy, "O")
                    if count == k:
                        return float('-inf')
                    elif count >= 1:
                        score -= 2 ** count

        if zHashing:
            self._zobristTable[self._zobristHash(state)] = score

        return score
    
    """
    Helper functions
    """

    # Get successors and moves for minimax
    def _successors_and_moves(self, state):
        b = state.board
        mCols = len(b[0])
        nRows = len(b)
        new_states = []

        for i in range(nRows):
            for j in range(mCols):
                if b[i][j] != ' ':
                    continue
                new_state = game_types.State(old=state)
                new_state.board[i][j] = state.whose_move
                new_state.change_turn()

                new_states.append(([i, j], new_state))

        return new_states
    
    # Used for computing value of a line in the static eval function
    def _check_line(self, board, m, n, k, start_x, start_y, dx, dy, who):
        count = 0
        x, y = start_x, start_y
        end_x, end_y = x + dx * (k - 1), y + dy * (k - 1)

        if 0 <= end_x < m and 0 <= end_y < n:
            for _ in range(k):
                if board[y][x] == who:
                    count += 1
                elif board[y][x] == " ":
                    count += 1 / (2 * k)
                else:
                    return 0
                x += dx
                y += dy

        return count
    
    # Used for utterances
    def _get_utterance(self, score, currentRemark):
        # Ask about the previous move or how the game is so far
        rng = random.randint(1, 40)
        if rng == 1:
            return "Hmm. Tell me how you did that."
        elif rng == 2:
            return self.opponent_nickname + ". What's your take on the game so far?"
        # General utterances about who's winning/losing the game or if both sides are equal.
        utt_text = "twin" if self.twin else "default"
        if score == 0:
            return random.choice(OurAgent.EQUAL_UTTERANCES[utt_text])
        if self.side == "X" and score > 0 or self.side == "O" and score < 0:
            return random.choice(OurAgent.WINNING_UTTERANCES[utt_text])
        else:
            return random.choice(OurAgent.LOSING_UTTERANCES[utt_text])
    
    # Compute the Zobrist hash code given a state
    def _zobristHash(self, state):
        val = 0
        m, n = self.game_type.m, self.game_type.n
        for y in range(n):
            for x in range(m):
                if state.board[y][x] == "X":
                    val ^= self.zobrist_nums[y][x][0]
                elif state.board[y][x] == 'O':
                    val ^= self.zobrist_nums[y][x][1]
        return val

 
# OPTIONAL THINGS TO KEEP TRACK OF:

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances

