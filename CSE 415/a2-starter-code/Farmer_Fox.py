'''Farmer_Fox.py
[STUDENTS: REPLACE THE FOLLOWING INFORMATION WITH YOUR
OWN:]
by Janet Jenson and Susan Lee
UWNetIDs: jjens17, suelee01
Student numbers: 1799999, 2599999

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

    def can_move(self, F, f, c, g):


# Put your OPERATORS section here.

class Operator:
    pass

# etc.


# Finish off with the GOAL_TEST and GOAL_MESSAGE_FUNCTION here.

