'''
besbati_KInARow.py
Authors: Besbati, Lucas

An agent for playing "K-in-a-Row with Forbidden Squares" and related games.
CSE 415, University of Washington

With Zobrist Hashing Implementation
'''

from agent_base import KAgent
from game_types import State, Game_Type

AUTHORS = 'Besbati, Lucas; Roy Lee' 
UWNETIDS = ['besbati, royl14']

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
import time
import game_types
import math
import random

INF = math.inf

# Create your own type of agent by subclassing KAgent:

class OurAgent(KAgent):
    def __init__(self, twin=False):
        self.twin = twin
        self.nickname = 'Peter'
        if twin: self.nickname += '2'
        self.long_name = 'Dinklebot'
        if twin: self.long_name += ' II'
        self.persona = 'blunt'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "X"
        self.alpha_beta_cutoffs_this_turn = -1
        self.num_static_evals_this_turn = -1
        self.zobrist_table_num_entries_this_turn = -1
        self.zobrist_table_num_hits_this_turn = -1
        self.current_game_type = None
        self.playing_mode = KAgent.DEMO
        self.llm_enabled = False
        self.llm = None
        
        # Zobrist hashing structures
        self.zobrist_table = {}  # Hash -> (depth, value, move)
        self.zobrist_keys = None  # Will be initialized in prepare()
        self.zobrist_writes = 0
        self.zobrist_read_attempts = 0
        self.zobrist_successful_reads = 0

    def introduce(self):
        intro = '\nMy name is Peter Dinklage, but you can call me Dinklebot.\n'+\
            '"Lucas Besbati" made me.\n'+\
            'I am back from the Destiny Content Vault to terrorize inferior agents.\n'+\
            'And burn down Bungie HQ... In-game of course.\n'
        if self.twin: intro += "I'm Dinklebot II, no relation.\n"
        return intro

    def prepare(
        self,
        game_type,
        what_side_to_play,
        opponent_nickname,
        expected_time_per_move=0.1,
        utterances_matter=True):
        
        if utterances_matter:
            genai.configure(api_key="AIzaSyDrcx3hW4x1cN2ZiV1ZrYTW8ENpZC3oTaQ")
            self.llm = genai.GenerativeModel('gemini-pro')
        
        self.current_game_type = game_type
        self.what_side_to_play = what_side_to_play
        self.time_limit = expected_time_per_move
        
        # Initialize Zobrist keys for this game type
        self._initialize_zobrist_keys(game_type.n, game_type.m)
        
        return "OK"
    
    def _initialize_zobrist_keys(self, n_rows, m_cols):
        """Initialize random Zobrist keys for each position and piece type"""
        random.seed(42)  # Use a fixed seed for consistency
        self.zobrist_keys = {}
        
        # Create random keys for X and O at each position
        for i in range(n_rows):
            for j in range(m_cols):
                self.zobrist_keys[(i, j, 'X')] = random.getrandbits(64)
                self.zobrist_keys[(i, j, 'O')] = random.getrandbits(64)
    
    def _compute_zobrist_hash(self, state):
        """Compute Zobrist hash for a given state"""
        hash_value = 0
        board = state.board
        
        for i in range(len(board)):
            for j in range(len(board[0])):
                piece = board[i][j]
                if piece in ['X', 'O']:
                    hash_value ^= self.zobrist_keys[(i, j, piece)]
        
        return hash_value
    
    def _lookup_zobrist(self, state, depth):
        """Look up a state in the Zobrist table"""
        self.zobrist_read_attempts += 1
        hash_value = self._compute_zobrist_hash(state)
        
        if hash_value in self.zobrist_table:
            stored_depth, stored_value, stored_move = self.zobrist_table[hash_value]
            # Only use if stored depth is >= current depth (more or equally thorough search)
            if stored_depth >= depth:
                self.zobrist_successful_reads += 1
                return stored_value, stored_move
        
        return None, None
    
    def _store_zobrist(self, state, depth, value, move):
        """Store a state evaluation in the Zobrist table"""
        hash_value = self._compute_zobrist_hash(state)
        
        # Only store if we don't have this position or if new search is deeper
        if hash_value not in self.zobrist_table or self.zobrist_table[hash_value][0] < depth:
            self.zobrist_table[hash_value] = (depth, value, move)
            self.zobrist_writes += 1

    def generate_utterance(self, game_state, opponent_said, my_move):
        """Generate contextual utterance"""
        
        # Fallback if no LLM
        if not self.llm_enabled:
            fallbacks = [
                "Calculated move.",
                "Let's see how this plays out.",
                "Strategic placement.",
                "That should work."
            ]
            import random
            return random.choice(fallbacks)
        
        # Build prompt
        x_count = sum(row.count('X') for row in game_state.board)
        o_count = sum(row.count('O') for row in game_state.board)

        eval_score = self.static_eval(game_state)
        if eval_score > 100:
            position = "I'm winning"
        elif eval_score < -100:
            position = "I'm losing"
        else:
            position = "It's even"
        
        prompt = f"""You are Dinklebot, sarcastic AI from Destiny.

    Game situation:
    - Board has {x_count} X's and {o_count} O's
    - Position: {position}
    - You just moved to position {my_move}
    - Opponent said: "{opponent_said}"

    Respond in 1-2 sentences. Be witty and in-character (sarcastic but not mean).

    Your response:"""
        
        try:
            response = self.llm.generate_content(prompt)
            return response.text.strip()
        except:
            return "Interesting move."
        
    def make_move(self, current_state, current_remark, time_limit=1000,
                    use_alpha_beta=True,
                    use_zobrist_hashing=False, max_ply=3,
                    special_static_eval_fn=None):
        print("make_move has been called")

        # Reset statistics for this turn
        self.alpha_beta_cutoffs_this_turn = 0
        self.num_static_evals_this_turn = 0
        self.zobrist_writes = 0
        self.zobrist_read_attempts = 0
        self.zobrist_successful_reads = 0
        
        # Clear Zobrist table if hashing is disabled
        if not use_zobrist_hashing:
            self.zobrist_table = {}

        # Use special static eval if in autograder mode
        original_static_eval = None
        if (self.playing_mode == KAgent.AUTOGRADER and special_static_eval_fn is not None):
            original_static_eval = self.static_eval
            self.static_eval = special_static_eval_fn
        
        print("Calling minimax, please defend me while I compute the value.")
        best_move, val = self.minimax(
            current_state, 
            max_ply, 
            use_alpha_beta,
            use_zobrist_hashing
        )
        
        # Restore original static eval
        if original_static_eval is not None:
            self.static_eval = original_static_eval
        
        if not best_move:
            print(current_state)
            print(val)
        
        new_state = do_move(current_state, best_move[0], best_move[1], other(current_state.whose_move))
        
        new_remark = self.generate_utterance(current_state, current_remark, best_move)

        # Update zobrist statistics
        self.zobrist_table_num_entries_this_turn = len(self.zobrist_table)
        self.zobrist_table_num_hits_this_turn = self.zobrist_successful_reads

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

    def minimax(self,
            state,
            depth_remaining,
            pruning=False,
            use_zobrist=False,
            alpha=-INF,
            beta=INF):
        
        # Check Zobrist table first if enabled
        if use_zobrist:
            cached_value, cached_move = self._lookup_zobrist(state, depth_remaining)
            if cached_value is not None:
                return cached_move, cached_value
        
        # Generate child states
        child_states = list(move_gen(state))
        
        # Evaluate current state
        self.num_static_evals_this_turn += 1
        current_eval = self.static_eval(state)

        # Base cases: depth 0 or terminal state
        if depth_remaining == 0 or not child_states or current_eval == INF or current_eval == -INF:
            return None, current_eval

        # Set up for maximizing or minimizing player
        if state.whose_move == "X":
            compare_function = lambda a, b: a >= b
            best_val = -INF
        else:  # "O" player
            compare_function = lambda a, b: a <= b
            best_val = INF
        
        best_move = None
        
        # Optional: Order children by static evaluation for better pruning
        if use_zobrist:
            # Check if children have cached values for ordering
            child_evals = []
            for move, child_state in child_states:
                cached_val, _ = self._lookup_zobrist(child_state, 0)
                if cached_val is not None:
                    child_evals.append((move, child_state, cached_val))
                else:
                    child_evals.append((move, child_state, self.static_eval(child_state)))
            
            # Sort based on whether we're maximizing or minimizing
            if state.whose_move == "X":
                child_evals.sort(key=lambda x: x[2], reverse=True)
            else:
                child_evals.sort(key=lambda x: x[2])
            
            child_states = [(move, child_state) for move, child_state, _ in child_evals]
        
        # Search through children
        for move, child_state in child_states:
            result = self.minimax(
                child_state, 
                depth_remaining - 1, 
                pruning=pruning,
                use_zobrist=use_zobrist,
                alpha=alpha, 
                beta=beta
            )
            child_val = result[1]

            if compare_function(child_val, best_val):
                if pruning:
                    if state.whose_move == "X":
                        alpha = max(alpha, child_val)
                    else:
                        beta = min(beta, child_val)
                    
                    if alpha >= beta:
                        self.alpha_beta_cutoffs_this_turn += 1
                        # Store in Zobrist table before returning
                        if use_zobrist:
                            self._store_zobrist(state, depth_remaining, child_val, move)
                        return move, child_val
                
                best_move = move
                best_val = child_val
        
        # Store result in Zobrist table
        if use_zobrist:
            self._store_zobrist(state, depth_remaining, best_val, best_move)
        
        return best_move, best_val

    def static_eval(self, state, game_type=None):
        board = state.board
        if game_type == None:
            game_type = self.current_game_type
        k = game_type.k
        mCols = game_type.m
        nRows = game_type.n

        eval_result = 0
        for i in range(nRows):
            eval_result += self.check_section(board, k, i, 0, 0, 1)  # row
            if eval_result == INF or eval_result == -INF:
                return eval_result
        for j in range(mCols):
            eval_result += self.check_section(board, k, 0, j, 1, 0)  # column
            if eval_result == INF or eval_result == -INF:
                return eval_result
            eval_result += self.check_section(board, k, 0, j, 1, 1)  # diag right
            if eval_result == INF or eval_result == -INF:
                return eval_result
            eval_result += self.check_section(board, k, 0, j, 1, -1)  # diag left
            if eval_result == INF or eval_result == -INF:
                return eval_result

        return eval_result
    
    def check_section(self, board, k, row, col, rowStep, colStep):
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
        while (rowStep * i + row < len(board) and colStep * i + col < len(board[0]) and colStep * i + col >= 0):
            curr = board[rowStep * i + row][colStep * i + col]
            if curr == ' ':
                rightSpaceStreak += 1
            elif curr == 'X' or curr == 'O':
                if curr != streakItem:
                    # conclude the last streak
                    eval += self.addScore(k, rightSpaceStreak, leftSpaceStreak, mainStreak, streakItem)
                    # switch to new streak
                    streakItem = curr
                    mainStreak = 1
                    leftSpaceStreak = rightSpaceStreak
                    rightSpaceStreak = 0
                else:
                    mainStreak += 1
                    if mainStreak == k:
                        if streakItem == 'X':
                            return INF
                        if streakItem == 'O':
                            return -INF
            else:
                # conclude the last streak
                eval += self.addScore(k, rightSpaceStreak, leftSpaceStreak, mainStreak, streakItem)
                # reset
                streakItem = ''
                mainStreak = 0
                leftSpaceStreak = 0
                rightSpaceStreak = 0
            i += 1
        
        # conclude the final streak if there is one
        eval += self.addScore(k, rightSpaceStreak, leftSpaceStreak, mainStreak, streakItem)
        
        return eval
    
    def addScore(self, k, rightSpaceStreak, leftSpaceStreak, mainStreak, streakItem):
        if mainStreak == 0:
            return 0
        addAmount = 0
        if rightSpaceStreak + leftSpaceStreak + mainStreak >= k:  # guarantee possible placement
            addAmount += pow(10, mainStreak)
            if rightSpaceStreak > 0 and leftSpaceStreak > 0:  # bonus points for both sides availability
                addAmount *= 2
        if streakItem == 'X':
            return addAmount
        else:
            return -addAmount


# Helper functions
def other(p):
    if p == 'X':
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