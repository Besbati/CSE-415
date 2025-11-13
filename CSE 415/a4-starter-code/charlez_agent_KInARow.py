'''
<yourUWNetID>_KInARow.py
Authors: Besbati, Lucas and Lee, Roy


An agent for playing "K-in-a-Row with Forbidden Squares" and related games.
CSE 415, University of Washington

THIS IS A TEMPLATE WITH STUBS FOR THE REQUIRED FUNCTIONS.
YOU CAN ADD WHATEVER ADDITIONAL FUNCTIONS YOU NEED IN ORDER
TO PROVIDE A GOOD STRUCTURE FOR YOUR IMPLEMENTATION.

'''

from agent_base import KAgent
from game_types import State, Game_Type
from charlez.charlez_staticEvals import expensive_staticEval, cheap_staticEval
from random import randint

AUTHORS = 'Lucas Besbati, Roy Lee' 
UWNETIDS = ['besbati'] # The first UWNetID here should
# match the one in the file name, e.g., janiesmith99_KInARow.py.

import time # You'll probably need this to avoid losing a
# game due to exceeding a time limit.
import game_types
import math

INF = math.inf
# Create your own type of agent by subclassing KAgent:

class OurAgent(KAgent):  # Keep the class name "OurAgent" so a game master
    # knows how to instantiate your agent class.

    def __init__(self, twin=False):
        self.twin=twin
        self.nickname = 'Strangler'
        if twin: self.nickname += '2'
        self.long_name = 'Tattletale Strangler'
        if twin: self.long_name += ' II'
        self.persona = 'edgy and violent'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "X" # e.g., "X" or "O".
        self.alpha_beta_cutoffs_this_turn = -1
        self.num_static_evals_this_turn = -1
        self.zobrist_table_num_entries_this_turn = -1
        self.zobrist_table_num_hits_this_turn = -1
        self.current_game_type = None
        self.playing_mode = KAgent.DEMO

    def introduce(self):
        intro = '\nMy name is the Tattletale Strangler.\n'+\
            'Charles made me (before I STRANGLED him).\n'+\
            'I\'m a violent criminal who strangles anyone who turns me in.\n'
        if self.twin:
            intro += 'Please!! I had to say that or else he\'d kill me!.\n'+\
                'I\'VE BEEN SET UP TO TAKE THE FALL!!'
        return intro

    
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

    # Receive and acknowledge information about the game from
    # the game master:
    def prepare(
        self,
        game_type,
        what_side_to_play,
        opponent_nickname,
        expected_time_per_move = 0.1, # Time limits can be
                                      # changed mid-game by the game master.

        utterances_matter=True):      # If False, just return 'OK' for each utterance,
                                      # or something simple and quick to compute
                                      # and do not import any LLM or special APIs.
                                      # During the tournament, this will be False..
       if utterances_matter:
           pass
           # Optionally, import your LLM API here.
           # Then you can use it to help create utterances.
           
       # Write code to save the relevant information in variables
       # local to this instance of the agent.
       # Game-type info can be in global variables.
       self.current_game_type = game_type
       self.what_side_to_play = what_side_to_play
       self.time_limit = expected_time_per_move

       # print("Change this to return 'OK' when ready to test the method.")
       return "OK"
   
    # The core of your agent's ability should be implemented here:             
    def make_move(self, current_state, current_remark, time_limit=1000,
                  use_alpha_beta=True,
                  use_zobrist_hashing=False, max_ply=3,
                  special_static_eval_fn=None):
        print("make_move has been called")

        print("code to compute a good move should go here.")

        self.alpha_beta_cutoffs_this_turn = 0
        self.num_static_evals_this_turn = 0

        original_static_eval = None
        if (self.playing_mode == KAgent.AUTOGRADER and special_static_eval_fn is not None):
            original_static_eval = self.static_eval
            self.static_eval = special_static_eval_fn
        
        best_move, val = self.minimax(current_state, max_ply, True)
        
        if original_static_eval is not None:
            self.static_eval = original_static_eval
        
        if not best_move:
            print(current_state)
            print(val)
        new_state = do_move(current_state, best_move[0], best_move[1], other(current_state.whose_move))
        # Here's a placeholder:
        # a_default_move = (0, 0)  This might be legal ONCE in a game,
        # if the square is not forbidden or already occupied.
    
        # new_state = current_state # This is not allowed, and even if
        # it were allowed, the newState should be a deep COPY of the old.

        new_remark = self._utterance(val, current_remark)

        if self.playing_mode == KAgent.AUTOGRADER:
            stats = [
                self.alpha_beta_cutoffs_this_turn, 
                self.num_static_evals_this_turn, 
                self.zobrist_table_num_entries_this_turn, 
                self.zobrist_table_num_hits_this_turn
            ]
            return [[best_move, new_state] + stats, new_remark]
        else:
            return [[best_move, new_state], new_remark]

    # The main adversarial search function:
    def minimax(self,
            state,
            depth_remaining,
            pruning=False,
            alpha=-INF,
            beta=INF):
        
        child_states = move_gen(state)
        self.num_static_evals_this_turn += 1
        current_eval = self.static_eval(state)

        if depth_remaining == 0 or not child_states:
            return None, current_eval

        if state.whose_move == "X":
            compare_function = lambda a, b: a >= b
            best_val = -INF
        else: # "O" player
            compare_function = lambda a, b: a <= b
            best_val = INF
        best_move = None
        for move, child_state in child_states:
            result = self.minimax(child_state, depth_remaining - 1, pruning = True, alpha = alpha, beta = beta)
            child_val = result[1]

            if compare_function(child_val, best_val):
                if pruning:
                    if state.whose_move == "X":
                        alpha = max(alpha, best_val)
                    else:
                        beta = min(beta, best_val)
                    if alpha >= beta:
                        self.alpha_beta_cutoffs_this_turn += 1
                        return move, child_val
                best_move = move
                best_val = child_val
        
        return best_move, best_val


        # default_score = 0 # Value of the passed-in state. Needs to be computed.

    
        # return [default_score, "my own optional stuff", "more of my stuff"]
        # Only the score is required here but other stuff can be returned
        # in the list, after the score, in case you want to pass info
        # back from recursive calls that might be used in your utterances,
        # etc. 
    

    # I went with the first static eval described in WE-2!
    def static_eval(self, state, game_type=None) -> float:
        if game_type ==None:
            game_type = self.current_game_type
        # Always increment this by 1.
        #self.static_eval_calls += 1
        #self.recent_static_eval_calls += 1
        # if zHashing:
        #     hash_val: int = self._zHash(state)
        #     # If it already exists in our Zobrist hash table, just return it!
        #     # Yes, this currently implementation doesn't resolve collisions.
        #     if hash_val in self.zTable:
        #         # A (presumably) successful zTable lookup!
        #         self.zHash_lookups += 1
        #         self.recent_zHash_lookups += 1
        #         return self.zTable.get(hash_val)

        # Not in our zTable? We have to do a computation.
        #self.static_eval_computations += 1
        #self.recent_static_eval_computations += 1
        val: float
        # As it turns out, I created two static evaluation functions.
        # As such, I can give the old one to my twin!
        if self.twin:
            val = cheap_staticEval(state)
        else:
            val = expensive_staticEval(state, game_type.k)
        # If using Zobrist hashing, insert the hashcode and value.
        # if zHashing:
        #     hash_val: int = self._zHash(state)
        #     self.zTable[hash_val] = val
        return val
    
    def addScore(self, k, rightSpaceStreak, leftSpaceStreak, mainStreak,streakItem):
        if mainStreak == 0:
            return 0
        addAmount = 0
        if rightSpaceStreak + leftSpaceStreak + mainStreak >= k: # guarantee possible placement
            addAmount += pow(10, mainStreak)
            if rightSpaceStreak > 0 and leftSpaceStreak > 0: # bonus points for both sides availability
                addAmount *= 2
        if streakItem == 'X':
            return addAmount
        else:
            return -addAmount
        


 
# OPTIONAL THINGS TO KEEP TRACK OF:
def other(p):
    if p =='X':
        return 'O'
    return 'X'

def move_gen(state):
    b = state.board
    p = state.whose_move
    o = other(p)
    mCols = len(b[0])
    nRows = len(b)

    for i in range(nRows):
        for j in range(mCols):
            if b[i][j] != ' ': 
                continue
            news = do_move(state, i, j, o)
            yield [(i, j), news]

def do_move(state, i, j, o):
    news = game_types.State(old=state)
    news.board[i][j] = state.whose_move
    news.whose_move = o
    return news

    

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances

