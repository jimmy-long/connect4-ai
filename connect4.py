import math
import numpy as np

RED = "R"
YELLOW = "Y"
EMPTY = None

BOARD_WIDTH = 7
BOARD_HEIGHT = 6

CENTER_WEIGHT = 3

MAX_THREE_IN_A_ROW_WEIGHT = 5
MAX_TWO_IN_A_ROW_WEIGHT = 2

MIN_THREE_IN_A_ROW_WEIGHT = -4
MIN_TWO_IN_A_ROW_WEIGHT = -1

def initial_board():
    """
    Generates a 7x7 Conncet 4 board with no pieces.
    """
    return np.full((BOARD_HEIGHT, BOARD_WIDTH), EMPTY)

def player(board):
    """
    Determines if it is the red or yellow players turn.
    Assumes that the red player plays first.
    """
    return YELLOW if (board == EMPTY).sum() % 2 == 0 else RED

def actions(board):
    """
    Returns a set of actions, represented as integers, representing the
    column the next piece would be dropped on - starting from 0.
    """
    possible_drop_cols = []

    # Only need to check the top row of the board, if a is empty it is possible to
    # drop a piece in the column.
    for col in range(len(board[0])):
        if board[0][col] is None:
            possible_drop_cols.append(col)

    return possible_drop_cols

def result(board, action):
    """
    Returns the board that results from the active player taking the specified action.
    Assumes the action is valid!!
    """
    new_board = np.copy(board)
    
    for row in reversed(range(0, BOARD_HEIGHT)):
        if board[row][action] == None:
            new_board[row][action] = player(board)
            break

    return new_board     

def winner(board):
    """
    Returns the winner of the game, or None if there is a draw, or no victor yet.
    Assumes the board is in a valid state.
    """
    directions = [(1,0), (1,-1), (1,1), (0,1)]
    for direction in directions:
        dx = direction[0]
        dy = direction[1]
        for x in range(BOARD_WIDTH):
            for y in range(BOARD_HEIGHT):
                lastx = x + (3 * dx)
                lasty = y + (3 * dy)
                if lastx >= 0 and lastx < BOARD_WIDTH:
                    if lasty >= 0 and lasty < BOARD_HEIGHT:
                        p = board[y][x]
                        if (p is not None and p == board[y + dy][x + dx]
                            and p == board[y + (2 * dy)][x + (2 * dx)] and p == board[lasty][lastx]):
                            return p
    
    return None

def terminal(board):
    """
    Returns a boolean value representing whether or not the board represents a terminal state.
    """
    if winner(board):
        return True

    return sum(1 for row in board for val in row if val is not None) == BOARD_WIDTH * BOARD_HEIGHT

def utility(board):
    """
    Returns 1 if red has won the game, -1 if yellow has won the game, or 0 otherwise.
    """
    game_winner = winner(board)
    
    # Handle the case of a board that has a winner.
    if game_winner == RED:
        return float("inf")
    elif game_winner == YELLOW:
        return float("-inf")
    
    # Build from 0.
    utility = 0

    # Score the center column - it is the most valuable.
    center_col = board[:, BOARD_WIDTH // 2]
    utility += (center_col == RED).sum() * CENTER_WEIGHT

    # Score row only positions
    for y in range(BOARD_HEIGHT):
        row = board[y,:]
        for x in range(BOARD_WIDTH - 3):
            board_slice = row[x : x + 4]
            utility += slice_utility(board_slice)

    # Score column only positions
    for x in range(BOARD_WIDTH):
        column = board[:,x]
        for y in range(BOARD_HEIGHT - 3):
            board_slice = column[y : y + 4]
            utility += slice_utility(board_slice)

    # Score diaogonal positions
    for y in range(BOARD_HEIGHT - 3):
        for x in range(BOARD_WIDTH - 3):
            # Top->Down and Left->Right
            board_slice = [board[y+i][x+i] for i in range(4)]
            utility += slice_utility(board_slice)

            # Down->Top and Left->Right
            board_slice = [board[y+3-i][x+i] for i in range(4)]
            utility += slice_utility(board_slice)

    return utility

def slice_utility(board_slice):
    utility = 0
    board_slice = np.array(board_slice)
    max_pieces = (board_slice == RED).sum()
    min_pieces = (board_slice == YELLOW).sum()

    # Increase utility if max has 2 or 3 positions in a slice that min has no pieces in.
    if max_pieces == 3 and min_pieces == 0:
        utility += MAX_THREE_IN_A_ROW_WEIGHT
    elif max_pieces == 2 and min_pieces == 0:
        utility += MAX_TWO_IN_A_ROW_WEIGHT

    # Decrease utility if min has 2 or 3 positions in a slice that max has no pieces in.
    if min_pieces == 3 and max_pieces == 0:
        utility += MIN_THREE_IN_A_ROW_WEIGHT
    elif min_pieces == 2 and max_pieces == 0:
        utility += MIN_TWO_IN_A_ROW_WEIGHT

    return utility


def minimax(board):
    """
    Returns the optimal move for the active player on the given baord.
    """
    return alphabeta(board, 5, float("-inf"), float("inf"))[1]

def alphabeta(board, depth, alpha, beta):
    """
    Constructs and searches a depth limited, alpha-beta pruned tree to determine
    the optimal move for the current player.

    Returns: A tuple of the form (value, best move)
    """
    if depth == 0 or terminal(board):
        return (utility(board), None)
    if player(board) == RED:
        value_action = (float("-inf"), None)
        for action in actions(board):
            # Find out what value is generated by exploring the resulting subtree.
            value_by_taking_action = alphabeta(result(board, action), depth - 1, alpha, beta)

            if value_by_taking_action[0] > value_action[0]:
                value_action = (value_by_taking_action[0], action)
            
            alpha = max(alpha, value_action[0])
            if alpha >= beta:
                break
        return value_action
    else:
        value_action = (float("inf"), None)
        for action in actions(board):
            value_by_taking_action = alphabeta(result(board, action), depth - 1, alpha, beta)

            if value_by_taking_action[0] < value_action[0]:
                value_action = (value_by_taking_action[0], action)

            beta = min(beta, value_action[0])
            if alpha >= beta:
                break
        return value_action

def main():
    print("Initializing empty board.")
    print("Are you red or yellow?")
    player = input()
    player = player.upper()[0]
    opp = RED if player == YELLOW else YELLOW
    print("Yellow goes first!")

    board = initial_board()
    player_turn = player == YELLOW
    running = True

    while running:
        move = None
        if player_turn:
            move = minimax(board)
            print("Drop your piece " + str(move) + " columns from the left hand side")
        else:
            print("What column did your opponent drop their piece in?")
            move = int(input())
        board = result(board, move)

        game_winner = winner(board)
        if game_winner is not None and game_winner == player:
            running = False
            print("Congratulations on crushing your opponent!")
        elif game_winner == opp:
            print("Sorry, your opponent was really good!")
            running = False

        player_turn = not player_turn

if __name__ == "__main__":
    main()

