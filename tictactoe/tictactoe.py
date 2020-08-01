#Solution Code to CS50 Ai course Tic tac toe's problem by Alberto Pascal Garza
#albertopascalgarza@gmail.com
"""
Tic Tac Toe Player
"""

import math
import copy
from random import randint

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    X_count = 0
    O_count = 0
    #to determine the turn, I will make a count of the X and O tokens on the board
    for row in board:
        #I create a dictionary with the count on each row
        player_turns = {i: row.count(i) for i in row}
        #I check if I have X and O tokens in the row, if not, create an entry with 0
        if not (player_turns.get("X")):
            player_turns['X'] = 0
        if not player_turns.get("O"):
            player_turns['O'] = 0
        #I add to my counter the total amount of tokens found for each player in this row
        X_count = X_count + int(player_turns['X'])
        O_count = O_count + int(player_turns['O'])

    #if X has the same amount of tokens than O, it means it is X's turn
    if(X_count == O_count):
        #It should be X's turn. 
        return "X"
    #Otherwise, it is O's turn.
    elif(X_count>O_count):
        #it is O's turn.
        return "O"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for row in range (0,len(board)):
        #these are the rows on my board
        for col in range (0,len(board[row])):
            #these are the columns on my board
            if(board[row][col] == EMPTY):
                #for each position, I check if it is empty. If it is, it is a possible spot for me to move next.
                actions.add((row,col))
                
    if len(actions)> 0:
        #if I have at least one possible action, I return them
        return actions
    else:
        #otherwise, I return EMPTY because there are no more possible actions
        return EMPTY


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    #we start by creating a deep copy of me board for me not to modify the original
    new_board = copy.deepcopy(board)
    #I get the player's turn in the current board.
    action_token = player(new_board)
    #If I the corresponding spot on my board is available
    if (new_board[action[0]][action[1]] == EMPTY):
        #then I will make that move with the current player
        new_board[action[0]][action[1]] = action_token
        return new_board
    else:
        #else, I raise a not a valid action error because the place is already taken or does not exist.
        raise Exception('Not a valid action')
    

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #To determine the winner, I need to know the board's final value. 
    token_value = utility(board)
    #if it's 1, X won. If it's -1, O won. Else, it was a tie.
    if(token_value == 1):
        return 'X'
    elif(token_value == -1):
        return 'O'
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    #I need to check if any won or if I don't have any spaces left
    game_ended = False
    found_empty = False
    #first of all, I check if I have empties.
    for row in board:
        if EMPTY in row:
            #if I do have empties, I flag it. It is likely that I have not finished yet.
            found_empty = True
    #we check on the rows and columns for a winner
    for i in range(0,3):
        if (board[i][0] == board[i][1] and board[i][0] == board[i][2] and (board[i][0] is not EMPTY)) or (board[0][i] == board[1][i] and board[0][i] == board[2][i] and (board[0][i] is not EMPTY)):
            game_ended = True
            #we flag the game as ended if there is a winner and break the loop.
            break
        else:
            #otherwise, we state that the game has no winners yet
            game_ended = False
    #If my game has no vertical or horizontal winners, I still have to check the diagonals.
    if not game_ended: 
        #there were no horizontal nor vertical wins. I need to check diagonals
        if (((board[0][0] == board[1][1] and board[2][2] == board[0][0]) or (board[0][2] == board[1][1] and board[2][0] == board[0][2]) ) and (board[1][1] is not EMPTY)):
            game_ended = True

    #Finally, if I found and empty and my game has no winners yet, it means I can keep playing
    if found_empty and not game_ended: 
        return False
    else:
        #otherwise, I have a winner and the game ended either due to a winner or a tie.
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    game_winner = ""
    #I will analyze every row first
    for i in range(0,3):
        #I check vertically and horizontally if the tokens are the same, meaning any of the two players has 3 in a row.
        if (board[i][0] == board[i][1] and board[i][0] == board[i][2] and (board[i][0] is not EMPTY)):
            #if I find a match vertically, I determine there was a winner and break the for cycle.
            game_winner = board[i][0]
            break
        elif (board[0][i] == board[1][i] and board[0][i] == board[2][i] and (board[0][i] is not EMPTY)):
             #if there is a match horizontally, I determine there was a winner and break the for cycle.
             game_winner = board[0][i]
             break
    #checking diagonals in case there were no winners neither vertically nor horizontally.
    if ((board[0][0] == board[1][1] and board[2][2] == board[0][0]) or (board[0][2] == board[1][1] and board[2][0] == board[0][2])) and (board[1][1] is not EMPTY):
            game_winner = board[1][1]
    #depending on my winning token, I will determine the value I should print. 
    if game_winner == "X":
        return 1
    elif game_winner == "O":
        return -1
    #Since we are assuming we will only receive terminal boards, if no winner was found, we have a tie and should return 0.
    else:
        return 0

def Max_Value(board):
    #I need to evaluate all of the possible options of actions for the board until I find the "max possible result"
    if(terminal(board)):
        #If my board is a terminal board, my value can only be the utility. 
        return utility(board)
    v = float('-inf')
    #otherwise, I will iterate amongst its actions, alternating on turns to see if I should get max or min values
    for action in actions(board):
        new_board = result(board, action)
        score = Min_Value(new_board)
        #I will store my maximum possible value amongst all of these "possible futures"
        v = max(v,score)
    return v
def Min_Value(board):
    #similar to max value, it will look for all of the possible actions until i find the one I find as "min possible result"
    if(terminal(board)):
        #if my board was terminal, I return my utility
        return utility(board)
    v = float('inf')
    #otherwise, I iterate on actions alternating turns
    for action in actions(board):
        new_board = result(board, action)
        score = Max_Value(new_board)
        #this time I will store the lowest value possible since I am O.
        v = min(v,score)
    return v
def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    #This function will return the best move. 
    #If Ai is playing as X, I can reduce the processing time by creating a random first move. 
    if (board == initial_state()):
        coord1 = randint(0,2)
        coord2 = randint(0,2)
        return ((coord1,coord2))
    #first I determine which player's turn it is
    player_to_move = player(board)
    best_action = None
    #If I am X
    if(player_to_move == "X"):
        current_max = float('-inf')
        #for every possible action I have right now, I'll call my "future" Min_Value since I will asume what will happen if I take this move.
        for action in actions(board):
            #peak on the future if I take that move
            curr_score = Min_Value(result(board,action))
            #if my future is favorable, I will store it as my current best option.
            if curr_score>= current_max:
                current_max = curr_score
                best_action = action
    else:
        #If I am O, I do something similar. 
        current_max = float('inf')
        #for every action I peak on the future for favorable results
        for action in actions(board):
            #this time, however, it would be X's turn so I need to start with Max_Value
            curr_score = Max_Value(result(board,action))
            #if my future is favorable, I store it
            if curr_score<= current_max:
                current_max = curr_score
                best_action = action
    #I return the best move.
    return best_action
   
