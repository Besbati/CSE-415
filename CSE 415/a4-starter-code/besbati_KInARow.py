'''
<yourUWNetID>_KInARow.py
Authors: Besbati, Lucas


An agent for playing "K-in-a-Row with Forbidden Squares" and related games.
CSE 415, University of Washington

THIS IS A TEMPLATE WITH STUBS FOR THE REQUIRED FUNCTIONS.
YOU CAN ADD WHATEVER ADDITIONAL FUNCTIONS YOU NEED IN ORDER
TO PROVIDE A GOOD STRUCTURE FOR YOUR IMPLEMENTATION.

'''

from agent_base import KAgent
from game_types import State, Game_Type

AUTHORS = 'Lucas Besbati' 
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
        
        best_move = None
        if current_state.whose_move == "X":
            best_val = -INF
        else:
            best_val = INF
        
        if use_alpha_beta:
            alpha = -INF
            beta = INF

            for move, child_state in move_gen(current_state):
                result = self.minimax(child_state, max_ply - 1, pruning=True, alpha=alpha, beta=beta)
                child_val = result[0]

                if current_state.whose_move == "X":
                    if child_val > best_val:
                        best_val = child_val
                        best_move = move
                    alpha = max(alpha, best_val)
                else:
                    if child_val < best_val:
                        best_val = child_val
                        best_move = move
                    beta = min(beta, best_val)
        else:
            for move, child_state in move_gen(current_state):
                result = self.minimax(child_state, max_ply - 1, pruning=False)
                child_val = result[0]
                
                if current_state.whose_move == "X":
                    if child_val > best_val:
                        best_val = child_val
                        best_move = move
                else:
                    if child_val < best_val:
                        best_val = child_val
                        best_move = move
        
        if original_static_eval is not None:
            self.static_eval = original_static_eval
        
        new_state = do_move(current_state, best_move[0], best_move[1], other(current_state.whose_move))
        # Here's a placeholder:
        # a_default_move = (0, 0)  This might be legal ONCE in a game,
        # if the square is not forbidden or already occupied.
    
        # new_state = current_state # This is not allowed, and even if
        # it were allowed, the newState should be a deep COPY of the old.
    
        new_remark = "I'm done... for now."

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
            alpha=None,
            beta=None):
        

        print("Calling minimax, please defend me while I compute the value.")
        if depth_remaining == 0: 
            self.num_static_evals_this_turn += 1
            return [self.static_eval(state)]
        
        # Code for when pruning == True
        if pruning:
            if alpha is None:
                alpha = -INF
            if beta is None:
                beta = INF

            if state.whose_move == "X":
                best_val = -INF
                for move, child_state in move_gen(state):
                    result = self.minimax(child_state, depth_remaining - 1, pruning = True, alpha = alpha, beta = beta)
                    child_val = result[0]

                    if child_val > best_val:
                        best_val = child_val

                    alpha = max(alpha, best_val)
                    if alpha >= beta:
                        self.alpha_beta_cutoffs_this_turn += 1
                        break

                return best_val
            
            else: # "O" player
                best_val = INF
                for (move, child_state) in move_gen(state):
                    result = self.minimax(child_state, depth_remaining - 1, pruning = True, alpha = alpha, beta = beta)
                    child_val = result[0]

                    if child_val < best_val:
                        best_val = child_val

                    beta = min(beta, best_val)
                    if alpha >= beta:
                        self.alpha_beta_cutoffs_this_turn += 1
                        break
                return best_val
            
        # minimax search no pruning 
        else:
            if state.whose_move == "X":
                best_val = -INF
            else:
                best_val = INF
            
            for (move, child_state) in move_gen(state):
                result = self.minimax(child_state, depth_remaining - 1, Pruning = False, alpha = None, beta = None)
                child_val = result[0]
                
                if ((state.whose_move == "X" and child_val > best_val) or (state.whose_move == "O" and child_val < best_val)):
                    best_val = child_val

            return best_val


        # default_score = 0 # Value of the passed-in state. Needs to be computed.

    
        # return [default_score, "my own optional stuff", "more of my stuff"]
        # Only the score is required here but other stuff can be returned
        # in the list, after the score, in case you want to pass info
        # back from recursive calls that might be used in your utterances,
        # etc. 
    

    def static_eval(self, state, game_type=None):
        board = state.board
        k = game_type.k
        mCols = game_type.m
        nRows = game_type.n

        eval_result = 0
        for i in range(nRows):
            eval_result += check_section(board, k, i, 0, 1, 0) # row
            eval_result += check_section(board, k, i, 0, 1, 1) # diag right
            eval_result += check_section(board, k, i, 0, -1, 1) # diag left
        for j in range(mCols):
            eval_result += check_section(board, k, 0, j, 0, 1) # column
        
        return eval_result
    
    def check_section(board, k, row, col, rowStep, colStep): # rowStep can be 1, 0 or -1, colstep 1 or 0
        if rowStep * k + row > len(board):
            return 0
        if colStep * k + col > len(board[0]):
            return 0
        eval = 0

        leftSpaceStreak = 0
        mainStreak = 0
        rightSpaceStreak = 0
        streakItem = ''

        i = 0
        while (rowStep * i + row < len(board) and colStep * i + col < len(board[0])):
            curr = board[rowStep * i + row][colStep * i + col]
            if curr == ' ':
                if mainStreak > 0: # X - < right side
                    rightSpaceStreak += 1
                else: # - X < left side
                    leftSpaceStreak += 1

            if curr == 'X' or curr == 'Y':
                if curr != streakItem: # - - - X - O
                    # conclude the last streak
                    addAmount = 0
                    if rightSpaceStreak + leftSpaceStreak + mainStreak >= k: # guarantee possible placement
                        addAmount += pow(10, streak)
                    if rightSpaceStreak > 0 and leftSpaceStreak > 0: # bonus points for both sides availability
                        addAmount *= 5
                    if streakItem == 'X':
                        eval += addAmount
                    if streakItem == 'Y':
                        eval -= addAmount
                    # switch to new streak
                    streakItem = curr
                    mainStreak = 1
                    leftSpaceStreak = rightSpaceStreak
                    rightSpaceStreak = 0

                if curr == streakItem:
                    streak += 1
                    if streak == k:
                        if streakItem == 'X':
                            eval += pow(10, streak)
                        if streakItem == 'Y':
                            eval -= pow(10, streak)
                        streakItem = ''
                        mainStreak = 0
                        leftSpaceStreak = 0
                        rightSpaceStreak = 0
            
            if curr == '-':
                # conclude the last streak
                addAmount = 0
                if rightSpaceStreak + leftSpaceStreak + mainStreak >= k: # guarantee possible placement
                    addAmount += pow(10, streak)
                if rightSpaceStreak > 0 and leftSpaceStreak > 0: # bonus points for both sides availability
                    addAmount *= 5
                if streakItem == 'X':
                    eval += addAmount
                if streakItem == 'Y':
                    eval -= addAmount
                # reset
                streakItem = ''
                mainStreak = 0
                leftSpaceStreak = 0
                rightSpaceStreak = 0
        
        # conclude the final streak if there is one
        addAmount = 0
        if rightSpaceStreak + leftSpaceStreak + mainStreak >= k: # guarantee possible placement
            addAmount += pow(10, streak)
        if rightSpaceStreak > 0 and leftSpaceStreak > 0: # bonus points for both sides availability
            addAmount *= 5
        if streakItem == 'X':
            eval += addAmount
        if streakItem == 'Y':
            eval -= addAmount
        
        return eval

        


 
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

