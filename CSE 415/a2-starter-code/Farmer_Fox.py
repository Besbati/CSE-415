'''Farmer_Fox.py
[STUDENTS: REPLACE THE FOLLOWING INFORMATION WITH YOUR
OWN:]
by Lucas Besbati and Roy Lee
UWNetIDs: besbati, royl14
Student numbers: 2224560, 2422916

Assignment 2, in CSE 415, Autumn 2025
 
This file contains my problem formulation for the problem of
the Farmer, Fox, Chicken, and Grain.
'''

# Put your formulation of the Farmer-Fox-Chicken-and-Grain problem here.
# Be sure your name(s), uwnetid(s), and 7-digit student number(s) are given above in 
# the format shown.

# You should model your code closely after the given example problem
# formulation in HumansRobotsFerry.py

# Put your metadata here, in the same format as in HumansRobotsFerry.
#<METADATA>
PROBLEM_NAME = "Farmer, Fox, Chicken, and Grain"
PROBLEM_VERSION = "1.1"
PROBLEM_AUTHORS = ['S. Tanimoto']
PROBLEM_CREATION_DATE = "10-JAN-2025"
#</METADATA>

# Start your Common Code section here.
#<COMMON_CODE>
LEFT = 0
RIGHT = 1
F = LEFT
f = LEFT
c = LEFT
g = LEFT




class State:

    # include methods similar to those in HumansRobotsFerry.py for
    # this class.

# Put your INITIAL STATE section here.
    def __init__(self, old = None):
        if old is None:
            self.F = LEFT
            self.f = LEFT
            self.c = LEFT
            self.g = LEFT
        else:
            self.F = old.F
            self.f = old.f
            self.c = old.c
            self.g = old.g

    def __eq__(self, s2):
        if self.F != s2.F: return False
        if self.f != s2.f: return False
        if self.c != s2.c: return False
        if self.g != s2.g: return False
        return True

    def __str__(self):
        txt = "\n Farmer is on the: " + str(self.F)+"\n"
        txt += "\n Fox is on the : " + str(self.f)+"\n"
        txt += "\n Chicken is on the: " + str(self.c)+"\n"
        txt += "\n Grain is on the: " + str(self.g)+"\n"
        return txt

    def __hash__(self):
        return (self.__str__()).__hash__()

    def copy(self):
        # Performs an appropriately deep copy of a state,
        # for use by operators in creating new states.
        return State(old=self)

    def can_move(self, s):
        # check if new state is legal
        if not self.is_legal(s):
            return False
        # check if farmer is moving alone
        if self.F != s.F and self.f == s.f and self.c == s.c and self.g == s.g:
            return True
        # check if farmer is moving more than one thing (fox and chicken, fox and grain, chicken and grain)
        if self.F != s.F and self.f != s.f and self.c != s.c and self.g == s.g:
            return False
        if self.F != s.F and self.f != s.f and self.c == s.c and self.g != s.g:
            return False
        if self.F != s.F and self.f == s.f and self.c != s.c and self.g != s.g:
            return False
        return True

    def is_legal(self, s):
        if s.f == s.c and s.F != s.f:
            return False
        if s.c == s.g and s.F != s.c:
            return False
        return True

    def move(self, s):
        news = self.copy()
        news.F = s.F
        news.f = s.f
        news.c = s.c
        news.g = s.g
        return news

    def is_goal(self):
        if self.F == RIGHT and self.f == RIGHT and self.c == RIGHT and self.g == RIGHT:
            return True
        else:
            return False

    def goal_message(s):
        return "Congratulations! You have successfully moved the fox, chicken, and grain to the other side!"

class Operator:
    def __init__(self, name, precond, state_transf):
        self.name = name
        self.precond = precond
        self.state_transf = state_transf

    def is_applicable(self, s):
        return self.precond(s)

    def apply(self, s):
        return self.state_transf(s)
#</COMMON_CODE>

#<INITIAL_STATE>
CREATE_INITIAL_STATE = lambda : State()
#</INITIAL_STATE>

# Put your OPERATORS section here.
#<OPERATORS>
OPERATORS = [
    Operator(
        "Farmer crosses alone",
        lambda s: s.can_move(1 - s.F, s.f, s.c, s.g),
        lambda s: s.move(1 - s.F, s.f, s.c, s.g)
    ),
    Operator(
        "Farmer crosses with fox",
        lambda s: s.can_move(1 - s.F, 1 - s.f, s.c, s.g),
        lambda s: s.move(1 - s.F, 1 - s.f, s.c, s.g)
    ),
    Operator(
        "Farmer crosses with chicken",
        lambda s: s.can_move(1 - s.F, s.f, 1 - s.c, s.g),
        lambda s: s.move(1 - s.F, s.f, 1 - s.c, s.g)
    ),
    Operator(
        "Farmer crosses with grain",
        lambda s: s.can_move(1 - s.F, s.f, s.c, 1 - s.g),
        lambda s: s.move(1 - s.F, s.f, s.c, 1 - s.g)
    )
]
#</OPERATORS>

# Finish off with the GOAL_TEST and GOAL_MESSAGE_FUNCTION here.
#<GOAL_TEST>
GOAL_TEST = lambda s: s.is_goal()
#</GOAL_TEST)

#<GOAL_MESSAGE_FUNCTION>
GOAL_MESSAGE = lambda s: s.goal_message()
#</GOAL_MESSAGE_FUNCTION>

