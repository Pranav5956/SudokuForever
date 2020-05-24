"""
This file consist of the sudoku solver and generation algorithm,
along with a sudoku class that can handle events.
"""

# Imports
from random import shuffle, randrange

# Make a list of numbers to choose from, to randomly fill the grid
AVAILABLE_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9]
AVAILABLE_POSITIONS = [(i, j) for j in range(9) for i in range(9)]

# Keep track of number of solutions to a given sudoku board
no_of_solutions = 0


def create_empty_sudoku_board():
    """
    Creates and returns an empty 9x9 Sudoku board
    :return: List[List[0]]
    """

    return [[0 for _ in range(9)] for _ in range(9)]


def create_duplicate_board(board):
    """
    Gets a board and returns a duplicate of the board, with a different memory address
    :param board: List[List[int]]
    :return: List[List[int]]
    """

    dup_board = create_empty_sudoku_board()
    for i, j in AVAILABLE_POSITIONS:
        dup_board[i][j] = board[i][j]
    return dup_board


def check_for_placement(board, x, y, n):
    """
    Check if n can be placed in the board at position (x,y)
    :param board: List[List[int]]
    :param x: int
    :param y: int
    :param n: int
    :return: bool
    """

    row_placement = n not in board[x]
    column_placement = n not in [board[i][y] for i in range(9)]
    box_placement = n not in [board[i][j] for i in range(x//3*3, x//3*3+3) for j in range(y//3*3, y//3*3+3)]

    return row_placement and column_placement and box_placement


def check_for_full_grid(board):
    """
    Checks if every position has a number filled
    :param board: List[List[int]]
    :return: bool
    """

    return 0 not in [board[x][y] for x, y in AVAILABLE_POSITIONS]


def solve_sudoku(board):
    """
    Solves a sudoku board using backtracking
    :param board: List[List[int]]
    :return: bool
    """

    # If the board is already full or is completely generated
    global no_of_solutions
    if check_for_full_grid(board):
        no_of_solutions += 1
        return True

    # Bring randomness to the board generation
    shuffle(AVAILABLE_NUMBERS)

    # Procedurally generate the numbers following the constraints of Sudoku
    for i, j in AVAILABLE_POSITIONS:
        if board[i][j] == 0:
            for n in AVAILABLE_NUMBERS:
                # Check if n is not in the row, column or in the corresponding 3x3 box
                if check_for_placement(board, i, j, n):
                    board[i][j] = n

                    if solve_sudoku(board):
                        return True

                    board[i][j] = 0

            return False


def generate_sudoku(board, n):
    """
    Procedurally removes n numbers from a solved sudoku grid to create a one-way solvable sudoku puzzle
    :param board: List[List[int]]
    :param n: int
    :return: None
    """

    global no_of_solutions
    free_positions = AVAILABLE_POSITIONS.copy()

    while n > 0:
        x, y = free_positions.pop(randrange(0, len(free_positions) - 1))
        temp_number = board[x][y]
        board[x][y] = 0

        # create a copy of the original board to send by copy
        temp_board = create_duplicate_board(board)

        # If the number of apparent solutions is 1, then proceed to remove the number
        no_of_solutions = 0
        solve_sudoku(temp_board)

        if no_of_solutions != 1:
            board[x][y] = temp_number
            free_positions.append((x, y))
        n -= 1


"""
This is the sudoku class that can handle input, marking, undo and redo operations.
This can be easily integrated with pygame to provide an interactive way of solving
the puzzle.
"""


class Sudoku:
    def __init__(self):
        """
        Initializes the Sudoku class
        """

        # Initialize attributes
        self.sudoku_completed = None
        self.sudoku_puzzle = None
        self.current_sudoku_puzzle = None
        self.entry_prohibition = None
        self.markings = None
        self.undo_history = []
        self.redo_history = []
        self.matching_numbers = None
        self.completion = {"Row": [], "Column": [], "Box": []}

        # Initialize flags and placeholders
        self.is_marking = False

    def initialize_puzzle(self, difficulty):
        """
        Initializes the puzzle, completed puzzle and states
        :param difficulty: int
        :return: None
        """

        self.difficulty = difficulty
        self.is_marking = False
        self.sudoku_completed = create_empty_sudoku_board()
        solve_sudoku(self.sudoku_completed)
        self.sudoku_puzzle = create_duplicate_board(self.sudoku_completed)
        generate_sudoku(self.sudoku_puzzle, self.difficulty)
        self.current_sudoku_puzzle = create_duplicate_board(self.sudoku_puzzle)

        if sum([self.sudoku_puzzle[x].count(0) for x in range(9)]) != self.difficulty:
            self.initialize_puzzle(self.difficulty)

        self.entry_prohibition = self._set_entry_prohibition()
        self.completion["Column"] = [1 if 0 not in self.current_sudoku_puzzle[r] else 0 for r in range(9)]
        self.completion["Row"] = [1 if 0 not in [self.current_sudoku_puzzle[r][c] for r in range(9)] else 0 for c in range(9)]
        self.completion["Box"] = [1 if 0 not in [self.current_sudoku_puzzle[x][y] for x in range(r, r+3) for y in range(c, c+3)]
                                  else 0 for c in range(0, 9, 3) for r in range(0, 9, 3)]

        self.markings = {(x, y): [] for x in range(9) for y in range(9) if (x, y) not in self.entry_prohibition}
        self.matching_numbers = {n: [] for n in range(1, 10)}

    def _set_entry_prohibition(self):
        """
        Sets the positions (x,y) where entries can be made
        :return: List[Tuple[int, int]]
        """

        return [(x, y) for x in range(9) for y in range(9) if self.sudoku_puzzle[x][y] != 0]

    def get_percentage_completion(self):
        """
        Returns the percentage of completion of the puzzle
        :return: float
        """

        correct_entries = 0
        for x in range(9):
            for y in range(9):
                if self.sudoku_puzzle[x][y] == 0:
                    correct_entries += (self.sudoku_completed[x][y] == self.current_sudoku_puzzle[x][y])
        return (correct_entries/self.difficulty)*100

    def _clear_all_histories(self):
        """
        Clears all undo and redo histories
        :return: None
        """

        self.redo_history = []
        self.undo_history = []

    def clear_data(self):
        """
        Clears all the data from the board
        :return: None
        """

        self.current_sudoku_puzzle = create_duplicate_board(self.sudoku_puzzle)
        self.markings = {(x, y): [] for x in range(9) for y in range(9) if (x, y) not in self.entry_prohibition}
        self._clear_all_histories()

    def get_wrong_entries(self):
        """
        Returns a list of wrong entries with their positions
        :return: List[Tuple]
        """

        wrong_entries = []
        for x in range(9):
            for y in range(9):
                if self.current_sudoku_puzzle[x][y] != 0 and self.current_sudoku_puzzle[x][y] != self.sudoku_completed[x][y]:
                    wrong_entries.append((x, y, self.current_sudoku_puzzle[x][y]))
        return wrong_entries

    def insert(self, x, y, n):
        """
        Inserts an entry into board (if not marking) or records the markings (if marking)
        :param x: int
        :param y: int
        :param n: int
        :return: None
        """

        if (x, y) not in self.entry_prohibition:
            if self.is_marking:
                if n not in self.markings[(x, y)]:
                    self.markings[(x, y)].append(n)
                    self.current_sudoku_puzzle[x][y] = 0
                    self.undo_history.append((x, y, self.is_marking, -1))
                else:
                    self.markings[(x, y)].remove(n)
                    self.undo_history.append((x, y, self.is_marking, n))
            else:
                self.undo_history.append((x, y, self.is_marking, self.current_sudoku_puzzle[x][y]))
                self.markings[(x, y)] = []
                self.current_sudoku_puzzle[x][y] = n

    def remove(self, x, y):
        """
        Removes an entry from the puzzle
        :param x: int
        :param y: int
        :return: None
        """

        if self.sudoku_puzzle[x][y] == 0:
            if self.is_marking:
                if self.markings[(x, y)]:
                    self.undo_history.append((x, y, self.is_marking, self.markings[(x, y)].pop()))
            else:
                if self.current_sudoku_puzzle[x][y] != 0:
                    self.undo_history.append((x, y, self.is_marking, self.current_sudoku_puzzle[x][y]))
                    self.current_sudoku_puzzle[x][y] = 0

    def undo(self):
        """
        Pop out the last action in the history and undo it
        Add the un-done action into the redo history
        :return: None
        """

        # Checks if there are moves to undo
        if self.undo_history:
            # Selects the current state's undo actions
            x, y, state, n = self.undo_history.pop()

            # Does operations based on current state
            if state:
                if n == -1:
                    if self.markings[(x, y)]:
                        self.redo_history.append((x, y, state, self.markings[(x, y)].pop()))
                else:
                    self.markings[(x, y)].append(n)
                    self.redo_history.append((x, y, state, -1))
            else:
                self.redo_history.append((x, y, state, self.current_sudoku_puzzle[x][y]))
                self.current_sudoku_puzzle[x][y] = n

    def redo(self):
        """
        Pop out the last action from the redo history and redo it
        Add the re-done action to the undo history
        :return:
        """

        # Checks if there are moves to redo
        if self.redo_history:
            # Selects the current state's redo actions
            x, y, state, n = self.redo_history.pop()

            # Does operations based on current state
            if state:
                if n == -1:
                    if self.markings[(x, y)]:
                        self.undo_history.append((x, y, state, self.markings[(x, y)].pop()))
                else:
                    self.markings[(x, y)].append(n)
                    self.undo_history.append((x, y, state, -1))
            else:
                self.undo_history.append((x, y, state, self.current_sudoku_puzzle[x][y]))
                self.current_sudoku_puzzle[x][y] = n
