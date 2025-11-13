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

AUTHORS = 'Lucas Besbati, Roy Lee' 
UWNETIDS = ['besbati'] # The first UWNetID here should
# match the one in the file name, e.g., janiesmith99_KInARow.py.
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (-1, 1)]
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
        self.nickname = 'Peter'
        if twin: self.nickname += '2'
        self.long_name = 'Dinklebot'
        if twin: self.long_name += ' II'
        self.persona = 'blunt'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "X" # e.g., "X" or "O".
        self.alpha_beta_cutoffs_this_turn = -1
        self.num_static_evals_this_turn = -1
        self.zobrist_table_num_entries_this_turn = -1
        self.zobrist_table_num_hits_this_turn = -1
        self.current_game_type = None
        self.playing_mode = KAgent.DEMO

    def introduce(self):
        intro = '\nMy name is Peter Dinklage, but you can call me Dinklebot.\n'+\
            '"Lucas Besbati" made me.\n'+\
            'I am back from the Destiny Content Vault to terrorize inferior agents.\n'+\
            'And burn down Bungie HQ... In-game of course.\n'
        if self.twin: intro += "I'm Dinklebot II, no relation.\n"
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
        
        print("Calling minimax, please defend me while I compute the value.")
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

        if self.playing == "X":
            compare_function = lambda a, b: a >= b
        else:
            compare_function = lambda a, b: a <= -b

        if compare_function(val, INF):
            new_remark = "Victory is mine!"
        elif compare_function(val, -INF):
            new_remark = "NO! I CANNOT LOSE!!"
        if val == 0:
            new_remark = "Evenly matched... for now."
        elif compare_function(val, 0):
            new_remark = "I will seize the advantage!"
        else:
            new_remark = "This agent is doing quite well... but not for long."

        if self.playing_mode == KAgent.AUTOGRADER:
            stats = [self.alpha_beta_cutoffs_this_turn, self.num_static_evals_this_turn, self.zobrist_table_num_entries_this_turn, self.zobrist_table_num_hits_this_turn]
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

        if depth_remaining == 0 or not child_states or current_eval == INF or current_eval == -INF:
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
                        return best_move, child_val
                best_move = move
                best_val = child_val
        
        return best_move, best_val


        # default_score = 0 # Value of the passed-in state. Needs to be computed.

    
        # return [default_score, "my own optional stuff", "more of my stuff"]
        # Only the score is required here but other stuff can be returned
        # in the list, after the score, in case you want to pass info
        # back from recursive calls that might be used in your utterances,
        # etc. 
    

    def static_eval(self, state, game_type=None):
        # Values should be higher when the states are better for X,
        # lower when better for O.
        #if zHashing:
        #    hash = self._zobristHash(state)
        #    if hash in self._zobristTable:
        #        return self._zobristTable.get(hash)
        score = 0
        board = state.board
        if game_type ==None:
            game_type = self.current_game_type
        k, m, n = game_type.k, game_type.m, game_type.n

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

        #if zHashing:
        #    self._zobristTable[self._zobristHash(state)] = score

        return score
    
    """
    Helper functions
    """
    
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

