import numpy as np
import copy
import time

NEW_NUM_DIST = np.array([2] * 9 + [4])
INIT_NUM_CELLS = 2
MOVES = ["h", "j", "k", "l"]
R_INVALID_MOVE = -1

class game():
    def __init__(self, N):
        """ make an NxN array and put numbers in two cells """
        self.N = N
        self.board = np.zeros((N, N))
        self.score = 0
        for _ in range(INIT_NUM_CELLS):
            self.add_num()
        print(self.board)

    def add_num(self):
        """
        self.board is a numpy array representing the game board
        add a random number according to NEW_NUM_DIST to one of
        the cells that are zero
        first need to check that there are at least one cell equal to zero
        """
        zero_inds = np.where(self.board == 0)
        num_zero_cells = zero_inds[0].size
        assert(num_zero_cells > 0)
        i = np.random.randint(num_zero_cells)
        self.board[zero_inds[0][i], zero_inds[1][i]] = np.random.choice(NEW_NUM_DIST)
        
    def left(self):
        """ change self.board to the state after a left move """
        for i in range(self.N):
            self.left_row(i)

    def right(self):
        """ change self.board to the state after a right move """
        for i in range(self.N):
            self.board[i] = self.board[i, ::-1]
            self.left_row(i)
            self.board[i] = self.board[i, ::-1]
    
    def up(self):
        """ change the board to the state after an up move """
        self.board = self.board.T
        self.left()
        self.board = self.board.T
        
    def down(self):
        """ change the board to the state after a down move """
        self.board = self.board.T
        self.right()
        self.board = self.board.T

    def left_row(self, i):
        """
        row is a 1d np array, possibly with zeros
        return a row with the state after a left move,
        which will merge cells with the same numbers
        """
        row = self.board[i]
        old_row = [x for x in row if x != 0]
        new_row, added_score = merge(old_row)
        new_row_array = np.zeros(row.size)
        new_row_array[:len(new_row)] = new_row
        self.board[i] = new_row_array
        self.score += added_score
    
    def can_move(self):
        """
        return true if there are zeros in the board
        or there are adjacent cells that are the same
        """
        for i in range(self.N):
            for j in range(self.N):
                # if any cell is equal to one of its neighbors then True
                if i - 1 >= 0:
                    if self.board[i - 1, j] == self.board[i, j]:
                        return True
                if i + 1 < self.N:
                    if self.board[i + 1, j] == self.board[i, j]:
                        return True
                if j - 1 >= 0:
                    if self.board[i, j - 1] == self.board[i, j]:
                        return True
                if j + 1 < self.N:
                    if self.board[i, j + 1] == self.board[i, j]:
                        return True
        if np.argwhere(self.board == 0).size != 0:
            # if there are any empty cells then True
            return True
        return False
    
    def change_state(self, key_in):
        """
        change the board to the state after the move
        and update the score accordingly
        """
        old_board = np.copy(self.board)
        old_score = self.score
        if key_in == "h":
            self.left()
        elif key_in == "j":
            self.down()
        elif key_in == "k":
            self.up()
        elif key_in == "l":
            self.right()
        else:
            pass
        if (self.board != old_board).any():
            # if the board changed, then add a new number to an empty cell. note that
            # the board might not change at all if we attemp to move in one direction
            # even though the board *can* be moved in some other direction
            self.add_num()
        return self.score - old_score

    def play_game(self):
        """
        ask for move, change state accordingly and print score and board, util
        no moves are allowed
        """
        i = 0
        while self.can_move():
            print(self.board, "score = ", self.score)
#             print("i = ", i)
            key_in = input("Enter direction (h, j, k, l): ")
            _ = self.change_state(key_in)
        print(self.board, "score = ", self.score)
        
    def board_str(self):
        """ convert the board to a unique string representation """
        return "".join([str(int(i)) for i in self.board.flatten()])
    
    def valid_action(self, key_in):
        """
        return True if the move can change the state of the board, otherwise
        False. use this for various search algorithms where we need to know
        if an action is allowed or not
        """
        g_copy = copy.deepcopy(self)
        _ = g_copy.change_state(key_in)
        return (g_copy.board != self.board).any()
    
    def get_valid_actions(self):
        valid_actions = []
        for move in MOVES:
            if self.valid_action(move):
                valid_actions.append(move)
        return valid_actions

def merge(old_row):
    """
    old_row and is a 1d list with no zeros
    new_row is the state after the left move,
    which will merge cells with the same numbers
    """
    new_row = []
    added_score = 0
    while len(old_row) >= 2:
        # if there are still at least two numbers in the old_row,
        # then try to merge the 0th and 1st numbers
        if old_row[0] == old_row[1]:
            new_row.append(old_row[0] * 2)
            added_score += old_row[0] * 2
            old_row = old_row[2:]
        else:
            new_row.append(old_row[0])
            old_row = old_row[1:]
    # len(old_row) should be either 0 or 1
    assert(len(old_row) <= 1)
    if len(old_row) == 1:
        new_row.append(old_row[0])
    return new_row, added_score


def tree_search_play(g, depth=5, n=1):
    """
    g is a game object, play the game using tree search until game.can_move() == false
    """
    i = 0
    while g.can_move():
        print(i)
        print(g.board, "score = ", g.score)
        move, _ = tree_search_move(g, depth=depth, n=n)
        print(move)
        _ = g.change_state(move)
        i += 1
        print()
    print(g.board, "score = ", g.score)


def tree_search_move(g, depth, n=1):
    """ perform tree search to find the move that increases g.score the most """
    assert(depth >= 1)
    scores = []
    for move in MOVES:
        if g.valid_action(move):
            # try move in a copy of the game
            g_copy = copy.deepcopy(g)
            added_score = g_copy.change_state(move)
            assert(added_score >= 0)
            if depth > 1:
                # if depth > 1, calculate the score from optimal actions with the
                # remaining depth and add to the added_score
                for i in range(n):
                    _, added_score_tmp = tree_search_move(g_copy, depth - 1, n=n)
                    added_score += added_score_tmp / n
            scores.append(added_score)
        else:
            # if move doesn't change the board at all, then don't select it
            scores.append(R_INVALID_MOVE)
    max_inds = [i for i, s in enumerate(scores) if s == max(scores)]
    ind = np.random.choice(max_inds)
    return MOVES[ind], max(scores)