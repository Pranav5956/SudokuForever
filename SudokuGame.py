"""
This file consists the entirety of the sudoku game itself
"""
# Handle imports
import pygame
from Sudoku import Sudoku
from enum import Enum
from math import trunc
import time


# Setting up state enums
class State(Enum):
    """
    This is an Enum class containing the list of states of the game
    """
    Intro = 0,
    DiffSelection = 1,
    Playing = 2,
    Paused = 3,
    Scores = 4


class Difficulty:
    """
    This is a class containing the difficulty values for the sudoku puzzle
    """
    Easy = 10
    Medium = 20
    Hard = 30
    Expert = 40


class Colors:
    """
    This is a class containing Colors in RGB Format
    """
    White = (255, 255, 255)
    Black = (0, 0, 0)
    AliceBlue = (227, 240, 255)
    BabyBlue = (140, 217, 255)
    Gainsboro = (219, 226, 236)
    Azure = (0, 127, 255)
    CrayolaPeriwinkle = (211, 224, 245)
    ImperialRed = (255, 10, 62)
    LightGray = (239, 245, 245)
    IndigoDye = (52, 70, 101)
    LightCoral = (255, 130, 134)


# The game object
class Game:
    """
    This is the master game object which controls the control flow of the game
    """
    def __init__(self):
        # PyGame Attributes
        self.window = None
        self.WIDTH = 825
        self.HEIGHT = 575
        self.GRID_PADDING = (50, 50)
        self.CELL_SIZE = 50
        self.state = State.Intro
        self.state_function = None
        self.current_highlighted_cell = None
        self.current_selected_cell = None
        self.current_highlighted_number = None
        self.current_highlighted_button = None
        self.grid = pygame.Rect(self.GRID_PADDING[0], self.GRID_PADDING[1], 9*self.CELL_SIZE, 9*self.CELL_SIZE)

        # Intro attributes
        self.intro_screen = pygame.image.load("Resources/SudokuForeverIntroPage.png")
        self.intro_countdown = 100

        # Diff selection attributes
        self.easy_box = (pygame.image.load("Resources/EasyBox.png"), pygame.image.load("Resources/EasyBoxHighlighted.png"))
        self.easy_box_rect = pygame.Rect(75, 75, 300, 175)
        self.easy_box_text = pygame.image.load("Resources/EasyBoxText.png")
        self.medium_box = (pygame.image.load("Resources/MediumBox.png"), pygame.image.load("Resources/MediumBoxHighlighted.png"))
        self.medium_box_rect = pygame.Rect(450, 75, 300, 175)
        self.medium_box_text = pygame.image.load("Resources/MediumBoxText.png")
        self.hard_box = (pygame.image.load("Resources/HardBox.png"), pygame.image.load("Resources/HardBoxHighlighted.png"))
        self.hard_box_rect = pygame.Rect(75, 325, 300, 175)
        self.hard_box_text = pygame.image.load("Resources/HardBoxText.png")
        self.expert_box = (pygame.image.load("Resources/ExpertBox.png"), pygame.image.load("Resources/ExpertBoxHighlighted.png"))
        self.expert_box_rect = pygame.Rect(450, 325, 300, 175)
        self.expert_box_text = pygame.image.load("Resources/ExpertBoxText.png")

        self.diff = {Difficulty.Easy: "EASY",
                     Difficulty.Medium: "MEDIUM",
                     Difficulty.Hard: "HARD",
                     Difficulty.Expert: "EXPERT"}
        self.diff_points = {Difficulty.Easy: 15000,
                            Difficulty.Medium: 30000,
                            Difficulty.Hard: 60000,
                            Difficulty.Expert: 120000}
        self.bonus = {Difficulty.Easy: 6000.00,
                      Difficulty.Medium: 15000.00,
                      Difficulty.Hard: 30000.00,
                      Difficulty.Expert: 60000.00}
        self.error = {Difficulty.Easy: 750,
                      Difficulty.Medium: 1500,
                      Difficulty.Hard: 3000,
                      Difficulty.Expert: 6000}
        self.error_count = 0
        self.error_deduction = 0
        self.current_bonus = 0

        # Pygame setup
        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Sudoku Forever!")
        self.sudoku_bg = pygame.image.load("Resources/SudokuBG.png")

        # Progress bar
        self.current_progress = 0
        self.progress_bar_rect = pygame.Rect(self.grid.x, self.grid.y + self.grid.height + 25 // 2, self.grid.width, 25)

        # Buttons
        self.small_play_button = (pygame.image.load("Resources/PlayButtonIdle.png"), pygame.image.load("Resources/PlayButtonActive.png"))
        self.big_play_button = pygame.image.load("Resources/PlayButton.png")
        self.small_pause_button = (pygame.image.load("Resources/PauseButtonIdle.png"), pygame.image.load("Resources/PauseButtonActive.png"))
        self.pause_toggle_rect = pygame.Rect(self.WIDTH - 11 - 32, 11, 32, 32)
        self.number_input_buttons_rect = pygame.Rect(2*self.GRID_PADDING[0] + 9*self.CELL_SIZE,
                                                     self.GRID_PADDING[1] + 9*self.CELL_SIZE//8,
                                                     9*self.CELL_SIZE//2, 9*self.CELL_SIZE//2)
        self.undo_button = pygame.image.load("Resources/UndoButton.png")
        self.undo_button_rect = pygame.Rect(self.number_input_buttons_rect.x,
                                            self.number_input_buttons_rect.y +
                                            self.number_input_buttons_rect.height - 1,
                                            self.undo_button.get_width() + 2, self.undo_button.get_height())
        self.redo_button = pygame.image.load("Resources/RedoButton.png")
        self.redo_button_rect = pygame.Rect(self.number_input_buttons_rect.x + 1 +
                                            self.number_input_buttons_rect.width//2,
                                            self.number_input_buttons_rect.y +
                                            self.number_input_buttons_rect.height - 1,
                                            self.redo_button.get_width(), self.redo_button.get_height())
        self.marking_button = pygame.image.load("Resources/MarkButton.png")
        self.marking_button_rect = pygame.Rect(self.undo_button_rect.x,
                                               self.undo_button_rect.y + self.undo_button_rect.height - 1,
                                               self.marking_button.get_width() + 2, self.marking_button.get_height())
        self.erase_button = pygame.image.load("Resources/EraseButton.png")
        self.erase_button_rect = pygame.Rect(self.marking_button_rect.x + self.marking_button_rect.width - 1,
                                             self.marking_button_rect.y,
                                             self.redo_button_rect.width, self.redo_button_rect.height)
        self.restart_button_rect = pygame.Rect(self.number_input_buttons_rect.x, self.grid.y,
                                               self.number_input_buttons_rect.width, 9*self.CELL_SIZE//8 - 10)
        self.newgame_button_rect = pygame.Rect(self.number_input_buttons_rect.x, self.progress_bar_rect.y - 3,
                                               self.number_input_buttons_rect.width, 9 * self.CELL_SIZE // 8 - 10)

        self.alert_timer = 0

        self.home_button = pygame.Rect(self.WIDTH//12, 4*self.HEIGHT//5, 2*self.WIDTH//9, self.HEIGHT//10)
        self.exit_button = pygame.Rect(self.WIDTH // 12 + 4*self.WIDTH//9 + 2*self.WIDTH//12, 4 * self.HEIGHT // 5,
                                       2*self.WIDTH // 9, self.HEIGHT // 10)

        # Fonts
        self.grid_font = pygame.font.SysFont("calibri", (3*self.CELL_SIZE)//5)
        self.number_font = pygame.font.SysFont("calibri", self.number_input_buttons_rect.width//5)
        self.button_font = pygame.font.SysFont("calibri", self.undo_button.get_height()//4)
        self.button_font2 = pygame.font.SysFont("calibri", (3*self.CELL_SIZE)//5, True)
        self.small_font = pygame.font.SysFont("calibri", 14, True)
        self.timer_font = pygame.font.SysFont("Calibri", self.pause_toggle_rect.width//2, True)
        self.heading_font = pygame.font.SysFont("calibri", self.number_input_buttons_rect.width//5, True)

        # Game attributes
        self.puzzle = Sudoku()
        self.not_ticking = True
        self.start_time = 0
        self.play_time = 0
        self.pause_start_time = 0
        self.pause_time = 0
        self.cum_pause_time = 0

        # Attributes
        self.score = 0

        self._draw()

    def _update_state_function(self):
        """
        Handle states an draw them
        :return: None
        """
        if self.state is State.Intro:
            self.state_function = self._draw_intro
        elif self.state is State.Playing:
            self.state_function = self._draw_playing
        elif self.state is State.Paused:
            self.state_function = self._draw_paused
        elif self.state is State.DiffSelection:
            self.state_function = self._draw_diff_selection
        elif self.state is State.Scores:
            self.state_function = self._draw_scores

    def _handle_events(self):
        """
        Handles a pygame event based on the current state
        :return: bool
        """
        # Handling events
        for event in pygame.event.get():
            # Quitting the game
            if event.type == pygame.QUIT:
                return False

            # Intro Events
            if self.state == State.Intro:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or \
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.state = State.DiffSelection

            # Difficulty selection events
            elif self.state == State.DiffSelection:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.easy_box_rect.collidepoint(event.pos):
                        self.difficulty = Difficulty.Easy
                        self.puzzle.initialize_puzzle(self.difficulty)
                        self.state = State.Playing

                    if self.medium_box_rect.collidepoint(event.pos):
                        self.difficulty = Difficulty.Medium
                        self.puzzle.initialize_puzzle(self.difficulty)
                        self.state = State.Playing

                    if self.hard_box_rect.collidepoint(event.pos):
                        self.difficulty = Difficulty.Hard
                        self.puzzle.initialize_puzzle(self.difficulty)
                        self.state = State.Playing

                    if self.expert_box_rect.collidepoint(event.pos):
                        self.difficulty = Difficulty.Expert
                        self.puzzle.initialize_puzzle(self.difficulty)
                        self.state = State.Playing

            # Playing Events
            elif self.state == State.Playing:
                # Keyboard inputs
                if event.type == pygame.KEYDOWN:
                    # Undo when ctrl+z is pressed
                    if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.puzzle.undo()
                    # Redo when ctrl+r is pressed
                    if event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.puzzle.redo()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.not_ticking and not \
                        self.pause_toggle_rect.collidepoint(event.pos):
                    self.start_time = time.time()
                    self.not_ticking = False

                # Check if the mouse is on the grid
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if self.grid.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_cell = (self.GRID_PADDING[0] +
                                                     (mouse_x - self.GRID_PADDING[0]) // self.CELL_SIZE * self.CELL_SIZE,
                                                     self.GRID_PADDING[1] +
                                                     (mouse_y - self.GRID_PADDING[1]) // self.CELL_SIZE * self.CELL_SIZE,
                                                     self.CELL_SIZE, self.CELL_SIZE)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.current_selected_cell = (self.GRID_PADDING[0] +
                                                      (mouse_x - self.GRID_PADDING[0]) // self.CELL_SIZE * self.CELL_SIZE,
                                                      self.GRID_PADDING[1] +
                                                      (mouse_y - self.GRID_PADDING[1]) // self.CELL_SIZE * self.CELL_SIZE,
                                                      self.CELL_SIZE, self.CELL_SIZE)
                # Pause button
                elif self.pause_toggle_rect.collidepoint(mouse_x, mouse_y):
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.state = State.Paused
                        self.pause_start_time = time.time()
                # Number buttons input
                elif self.number_input_buttons_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_button = None
                    self.current_highlighted_number = pygame.Rect(self.number_input_buttons_rect.x +
                                                                  (mouse_x-self.number_input_buttons_rect.x) //
                                                                  (self.number_input_buttons_rect.width//3) *
                                                                  self.number_input_buttons_rect.width//3,
                                                                  self.number_input_buttons_rect.y +
                                                                  (mouse_y - self.number_input_buttons_rect.y) //
                                                                  (self.number_input_buttons_rect.height // 3) *
                                                                  self.number_input_buttons_rect.height // 3,
                                                                  self.number_input_buttons_rect.height//3,
                                                                  self.number_input_buttons_rect.height//3)

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        number = (mouse_x - self.number_input_buttons_rect.x)//(self.number_input_buttons_rect.width//3) + \
                                 (mouse_y - self.number_input_buttons_rect.y)//(self.number_input_buttons_rect.height//3)*3 + 1
                        if self.current_selected_cell:
                            x, y = (self.current_selected_cell[0] - self.GRID_PADDING[0])//self.CELL_SIZE, \
                                   (self.current_selected_cell[1] - self.GRID_PADDING[1])//self.CELL_SIZE
                            self.puzzle.insert(x, y, number)
                            if self.puzzle.current_sudoku_puzzle[x][y] != self.puzzle.sudoku_completed[x][y]:
                                self.error_count += 1
                        else:
                            self.alert_timer = 750

                # Undo Button
                elif self.undo_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_number = None
                    self.current_highlighted_button = self.undo_button_rect
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.puzzle.undo()
                # Redo Button
                elif self.redo_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_number = None
                    self.current_highlighted_button = self.redo_button_rect
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.puzzle.redo()

                # Mark Button
                elif self.marking_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_button = self.marking_button_rect
                    self.current_highlighted_number = None
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.puzzle.is_marking = not self.puzzle.is_marking

                # Erase Button
                elif self.erase_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_button = self.erase_button_rect
                    self.current_highlighted_number = None
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.current_selected_cell:
                            self.puzzle.remove((self.current_selected_cell[0]-self.grid.x)//self.CELL_SIZE,
                                               (self.current_selected_cell[1]-self.grid.y)//self.CELL_SIZE)

                # Restart Button
                elif self.restart_button_rect.collidepoint(mouse_x, mouse_y):
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.puzzle.clear_data()
                        time.sleep(0.5)
                        self.start_time = 0
                        self.play_time = 0
                        self.pause_time = 0
                        self.pause_start_time = 0
                        self.cum_pause_time = 0
                        self.not_ticking = True
                        self.error_count = 0
                        self.error_deduction = 0

                # Newgame Button
                elif self.newgame_button_rect.collidepoint(mouse_x, mouse_y):
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.puzzle.initialize_puzzle(self.difficulty)
                        time.sleep(0.5)
                        self.start_time = 0
                        self.play_time = 0
                        self.pause_time = 0
                        self.pause_start_time = 0
                        self.cum_pause_time = 0
                        self.not_ticking = True
                        self.error_count = 0
                        self.error_deduction = 0

                # Otherwise just remove the highlighted cell
                else:
                    self.current_highlighted_cell = None
                    self.current_highlighted_number = None
                    self.current_highlighted_button = None

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.current_selected_cell = None

            # Paused Events
            elif self.state == State.Paused:
                # Un-pause methods
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.grid.collidepoint(event.pos) \
                            or self.pause_toggle_rect.collidepoint(event.pos)\
                            or self.number_input_buttons_rect.collidepoint(event.pos)\
                            or self.undo_button_rect.collidepoint(event.pos)\
                            or self.redo_button_rect.collidepoint(event.pos)\
                            or self.marking_button_rect.collidepoint(event.pos)\
                            or self.restart_button_rect.collidepoint(event.pos)\
                            or self.newgame_button_rect.collidepoint(event.pos):
                        if not self.start_time == 0:
                            self.cum_pause_time += self.pause_time
                        self.state = State.Playing

                mouse_x, mouse_y = pygame.mouse.get_pos()
                if self.number_input_buttons_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_button = None
                    self.current_highlighted_number = pygame.Rect(self.number_input_buttons_rect.x +
                                                                  (mouse_x-self.number_input_buttons_rect.x) //
                                                                  (self.number_input_buttons_rect.width//3) *
                                                                  self.number_input_buttons_rect.width//3,
                                                                  self.number_input_buttons_rect.y +
                                                                  (mouse_y - self.number_input_buttons_rect.y) //
                                                                  (self.number_input_buttons_rect.height // 3) *
                                                                  self.number_input_buttons_rect.height // 3,
                                                                  self.number_input_buttons_rect.height//3,
                                                                  self.number_input_buttons_rect.height//3)

                # Undo button
                elif self.undo_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_button = self.undo_button_rect
                    self.current_highlighted_number = None

                # Redo Button
                elif self.redo_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_button = self.redo_button_rect
                    self.current_highlighted_number = None

                # Mark Button
                elif self.marking_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_button = self.marking_button_rect
                    self.current_highlighted_number = None

                # Erase Button
                elif self.erase_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_button = self.erase_button_rect
                    self.current_highlighted_number = None

                # Restart Button
                elif self.restart_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_number = None

                # Newgame Button
                elif self.newgame_button_rect.collidepoint(mouse_x, mouse_y):
                    self.current_highlighted_number = None

                else:
                    self.current_highlighted_number = None
                    self.current_highlighted_button = None

            elif self.state is State.Scores:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.home_button.collidepoint(event.pos):
                        self.state = State.DiffSelection
                        self.start_time = 0
                        self.play_time = 0
                        self.pause_time = 0
                        self.pause_start_time = 0
                        self.cum_pause_time = 0
                        self.not_ticking = True
                        self.error_count = 0
                        self.error_deduction = 0
                        self.current_progress = 0
                        self.current_selected_cell = None
                        self.error_count = 0
                        self.error_deduction = 0
                    elif self.exit_button.collidepoint(event.pos):
                        return False

            # TODO: HighScore Events

        return True

    def _draw_intro(self):
        """
        Handles all the drawing activities in the Intro state
        :return: None
        """
        self.intro_countdown -= 1
        if self.intro_countdown < 0:
            self.intro_countdown = 100

        # Draw the intro screen
        self.window.blit(self.intro_screen, (0, 0))

        # Draw the intro screen text
        text = self.button_font2.render("CLICK TO PLAY!", True, Colors.Black)
        if self.intro_countdown >= 50:
            self.window.blit(text, (self.WIDTH//2 - text.get_width()//2, 5*self.HEIGHT//6 - text.get_height()//2))

    def _draw_diff_selection(self):
        """
        Handles all the drawing activities in the Difficulty Selection state
        :return: None
        """
        # Draw the text boxes
        self.window.blit(self.sudoku_bg, (0, 0))
        self.window.blit(self.easy_box[self.easy_box_rect.collidepoint(pygame.mouse.get_pos())], self.easy_box_rect[:2])
        self.window.blit(self.medium_box[self.medium_box_rect.collidepoint(pygame.mouse.get_pos())],
                         self.medium_box_rect[:2])
        self.window.blit(self.hard_box[self.hard_box_rect.collidepoint(pygame.mouse.get_pos())], self.hard_box_rect[:2])
        self.window.blit(self.expert_box[self.expert_box_rect.collidepoint(pygame.mouse.get_pos())], self.expert_box_rect[:2])

        self.window.blit(self.easy_box_text, self.easy_box_rect[:2])
        self.window.blit(self.medium_box_text, self.medium_box_rect[:2])
        self.window.blit(self.hard_box_text, self.hard_box_rect[:2])
        self.window.blit(self.expert_box_text, self.expert_box_rect[:2])

    def _draw_playing(self):
        """
        Handles all the drawing activities in the Playing state
        :return: None
        """
        # Set bg
        self.window.blit(self.sudoku_bg, (0, 0))
        pygame.draw.rect(self.window, Colors.White, self.grid)
        pygame.draw.rect(self.window, Colors.White, self.number_input_buttons_rect)
        pygame.draw.rect(self.window, Colors.White, self.progress_bar_rect)
        pygame.draw.rect(self.window, Colors.White, (self.undo_button_rect.x, self.undo_button_rect.y,
                                                     self.number_input_buttons_rect.width, self.number_input_buttons_rect.height))

        # Update the timer
        self.play_time = round(time.time() - self.start_time - self.cum_pause_time, 2)

        # Draw the current cell that the mouse is hovering over
        if self.current_highlighted_cell:
            pygame.draw.rect(self.window, Colors.AliceBlue, self.current_highlighted_cell)

        # Draw the currently selected cell and its corresponding rows, columns, boxes and boxes with the same digit
        if self.current_selected_cell:
            x, y = self.current_selected_cell[:2]
            pygame.draw.rect(self.window, Colors.Gainsboro,
                             (self.GRID_PADDING[0], y, 9*self.CELL_SIZE, self.CELL_SIZE))
            pygame.draw.rect(self.window, Colors.Gainsboro,
                             (x, self.GRID_PADDING[1], self.CELL_SIZE, 9*self.CELL_SIZE))
            pygame.draw.rect(self.window, Colors.Gainsboro,
                             (self.GRID_PADDING[0] + (x-self.GRID_PADDING[0])//(3*self.CELL_SIZE)*(3*self.CELL_SIZE),
                              self.GRID_PADDING[1] + (y-self.GRID_PADDING[1])//(3*self.CELL_SIZE)*(3*self.CELL_SIZE),
                              self.CELL_SIZE*3, self.CELL_SIZE*3))

            x, y = (x-self.GRID_PADDING[0])//self.CELL_SIZE, (y-self.GRID_PADDING[1])//self.CELL_SIZE

            # Same numbered boxes
            if self.puzzle.current_sudoku_puzzle[x][y] != 0:
                sim_cells = [(self.GRID_PADDING[0] + i*self.CELL_SIZE, self.GRID_PADDING[1] + j*self.CELL_SIZE,
                              self.CELL_SIZE, self.CELL_SIZE)
                             for i in range(9) for j in range(9)
                             if self.puzzle.current_sudoku_puzzle[i][j] == self.puzzle.current_sudoku_puzzle[x][y]]
                for cell in sim_cells:
                    pygame.draw.rect(self.window, Colors.CrayolaPeriwinkle, cell)

            # The selected box
            pygame.draw.rect(self.window, Colors.BabyBlue, self.current_selected_cell)

        # Draw a red box for wrong entries
        wrong_number_entries = self.puzzle.get_wrong_entries()
        for wrong_entry in wrong_number_entries:
            # Clash in column
            clash_column = [pygame.Rect(self.GRID_PADDING[0] + wrong_entry[0]*self.CELL_SIZE,
                                        self.GRID_PADDING[1] + y*self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                            for y in range(9) if wrong_entry[2] == self.puzzle.current_sudoku_puzzle[wrong_entry[0]][y]
                            and not (wrong_entry[0], y) == (wrong_entry[0], wrong_entry[1])]
            # Clash in row
            clash_row = [pygame.Rect(self.GRID_PADDING[0] + x*self.CELL_SIZE,
                                     self.GRID_PADDING[1] + wrong_entry[1]*self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                         for x in range(9) if wrong_entry[2] == self.puzzle.current_sudoku_puzzle[x][wrong_entry[1]]
                         and not (x, wrong_entry[1]) == (wrong_entry[0], wrong_entry[1])]

            # Clash in box
            clash_box = [pygame.Rect(self.GRID_PADDING[0] + x*self.CELL_SIZE,
                                     self.GRID_PADDING[1] + y*self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                         for x in range(wrong_entry[0]//3*3, wrong_entry[0]//3*3+3)
                         for y in range(wrong_entry[1]//3*3, wrong_entry[1]//3*3+3)
                         if wrong_entry[2] == self.puzzle.current_sudoku_puzzle[x][y]
                         and not (x, y) == (wrong_entry[0], wrong_entry[1])]

            for box in clash_box + clash_column + clash_row:
                pygame.draw.rect(self.window, Colors.LightCoral, box)

        # Drawing the grid
        for i in range(10):
            pygame.draw.line(self.window, Colors.Black,
                             (self.GRID_PADDING[0] + (i * self.CELL_SIZE), self.GRID_PADDING[1]),
                             (self.GRID_PADDING[0] + (i * self.CELL_SIZE), self.GRID_PADDING[1] + (9 * self.CELL_SIZE)),
                             (i % 3 == 0) + 1)
            pygame.draw.line(self.window, Colors.Black,
                             (self.GRID_PADDING[0], self.GRID_PADDING[1] + (i * self.CELL_SIZE)),
                             (self.GRID_PADDING[0] + (9 * self.CELL_SIZE), self.GRID_PADDING[1] + (i * self.CELL_SIZE)),
                             (i % 3 == 0) + 1)

        # Drawing the numbers on the grid
        for x in range(9):
            for y in range(9):
                # If it is not empty
                if self.puzzle.current_sudoku_puzzle[x][y] != 0:
                    # If it is a non-block number
                    if self.puzzle.sudoku_puzzle[x][y] == 0:
                        if not self.puzzle.current_sudoku_puzzle[x][y] == self.puzzle.sudoku_completed[x][y]:
                            num = self.grid_font.render(str(self.puzzle.current_sudoku_puzzle[x][y]), True, Colors.ImperialRed)
                        else:
                            # Display right number in blue
                            num = self.grid_font.render(str(self.puzzle.current_sudoku_puzzle[x][y]), True, Colors.Azure)
                    else:
                        # Display block number in Black
                        num = self.grid_font.render(str(self.puzzle.current_sudoku_puzzle[x][y]), True, Colors.Black)
                    # Draw the number with the appropriate color
                    self.window.blit(num,
                                     (self.GRID_PADDING[0] + self.CELL_SIZE//2 + x*self.CELL_SIZE - num.get_width()//2,
                                      self.GRID_PADDING[1] + self.CELL_SIZE//2 + y*self.CELL_SIZE - num.get_height()//3))
                elif (x, y) in self.puzzle.markings:
                    for n in self.puzzle.markings[(x, y)]:
                        num = self.small_font.render(str(n), True, Colors.IndigoDye)
                        self.window.blit(num, (self.grid.x + x * self.CELL_SIZE + (2 * ((n - 1) % 3 + 1) - 1) * self.CELL_SIZE // 6
                                               - num.get_width()//2,
                                               2 + self.grid.y + y * self.CELL_SIZE + (2 * ((n - 1) // 3) + 1) * self.CELL_SIZE // 6
                                               - num.get_height() // 2))

        # Small Pause Button
        self.window.blit(self.small_pause_button[self.pause_toggle_rect.collidepoint(pygame.mouse.get_pos())],
                         (self.pause_toggle_rect.x, self.pause_toggle_rect.y))

        # Drawing the buttons
        if self.current_highlighted_number:
            pygame.draw.rect(self.window, Colors.LightGray, self.current_highlighted_number)
        pygame.draw.rect(self.window, Colors.Black, self.number_input_buttons_rect, 1)
        for i in range(3):
            pygame.draw.line(self.window, Colors.Black,
                             (self.number_input_buttons_rect.x + i * self.number_input_buttons_rect.width // 3,
                              self.number_input_buttons_rect.y),
                             (self.number_input_buttons_rect.x + i * self.number_input_buttons_rect.width // 3,
                              self.number_input_buttons_rect.y + self.number_input_buttons_rect.height))
            pygame.draw.line(self.window, Colors.Black,
                             (self.number_input_buttons_rect.x,
                              self.number_input_buttons_rect.y + i * self.number_input_buttons_rect.width // 3),
                             (self.number_input_buttons_rect.x + self.number_input_buttons_rect.width,
                              self.number_input_buttons_rect.y + i * self.number_input_buttons_rect.width // 3))

        if self.current_highlighted_button:
            pygame.draw.rect(self.window, Colors.LightGray, self.current_highlighted_button)
        # Undo button
        self.window.blit(self.undo_button, (self.number_input_buttons_rect.x,
                                            self.number_input_buttons_rect.y + self.number_input_buttons_rect.height))
        pygame.draw.rect(self.window, Colors.Black, self.undo_button_rect, 1)

        # Redo Button
        self.window.blit(self.redo_button, (self.number_input_buttons_rect.x + 1 + self.number_input_buttons_rect.width//2,
                                            self.number_input_buttons_rect.y + self.number_input_buttons_rect.height))
        pygame.draw.rect(self.window, Colors.Black, self.redo_button_rect, 1)

        # Mark Button
        self.window.blit(self.marking_button, (self.marking_button_rect.x, self.marking_button_rect.y))
        pygame.draw.rect(self.window, Colors.Black, self.marking_button_rect, 1)

        # Erase Button
        self.window.blit(self.erase_button, (self.erase_button_rect.x, self.erase_button_rect.y))
        pygame.draw.rect(self.window, Colors.Black, self.erase_button_rect, 1)

        # Restart Button
        pygame.draw.rect(self.window, Colors.Azure, self.restart_button_rect)
        pygame.draw.rect(self.window, Colors.IndigoDye, self.restart_button_rect, 1)

        # New Game Button
        pygame.draw.rect(self.window, Colors.ImperialRed, self.newgame_button_rect)
        pygame.draw.rect(self.window, Colors.Black, self.newgame_button_rect, 1)

        # Drawing numbers on the buttons
        for i in range(3):
            for j in range(3):
                number = self.number_font.render(str(3 * i + j + 1), True, Colors.Black)
                self.window.blit(number,
                                 ((self.number_input_buttons_rect.x + (2 * j + 1) * self.number_input_buttons_rect.width // 6 -
                                   number.get_width() // 2),
                                  (self.number_input_buttons_rect.y + (2 * i + 1) * self.number_input_buttons_rect.width // 6 -
                                   number.get_height() // 3)))
        # Undo text
        text = self.button_font.render("UNDO", True, Colors.Black)
        self.window.blit(text, (self.undo_button_rect.x + self.undo_button.get_width()//2 - text.get_width()//2,
                                self.undo_button_rect.y + 5*self.undo_button.get_height()//6 - text.get_height()//2 + 3))
        # Redo text
        text = self.button_font.render("REDO", True, Colors.Black)
        self.window.blit(text, (self.redo_button_rect.x + 2 + self.redo_button.get_width() // 2 - text.get_width() // 2,
                                self.redo_button_rect.y + 5 * self.undo_button.get_height() // 6 - text.get_height() // 2 + 3))

        # Mark text
        text = self.button_font.render("MARK", True, Colors.Black)
        self.window.blit(text, (self.marking_button_rect.x + self.marking_button_rect.width//2 - text.get_width()//2,
                                self.marking_button_rect.y + 5 * self.marking_button_rect.height//6 - text.get_height() // 2 + 3))
        if self.puzzle.is_marking:
            text = self.small_font.render("ON", True, Colors.White)
            pygame.draw.ellipse(self.window, Colors.Azure, (self.marking_button_rect.x + 84 - text.get_width(),
                                                            self.marking_button_rect.y + 48 - text.get_height(),
                                                            2 * text.get_width(), 2 * text.get_height()))
            self.window.blit(text, (self.marking_button_rect.x + 84 - text.get_width() // 2,
                                    self.marking_button_rect.y + 48 - text.get_height() // 2))
        else:
            text = self.small_font.render("OFF", True, Colors.Black)
            pygame.draw.ellipse(self.window, Colors.Gainsboro, (self.marking_button_rect.x + 84 - text.get_width(),
                                                                self.marking_button_rect.y + 48 - text.get_height(),
                                                                2 * text.get_width(), 2 * text.get_height()))
            self.window.blit(text, (self.marking_button_rect.x + 84 - text.get_width() // 2,
                                    self.marking_button_rect.y + 48 - text.get_height() // 2))

        # Error calc
        self.error_deduction = self.error_count * self.error[self.difficulty]

        # Erase text
        text = self.button_font.render("ERASE", True, Colors.Black)
        self.window.blit(text, (self.erase_button_rect.x + 2 + self.erase_button_rect.width // 2 - text.get_width() // 2,
                                self.erase_button_rect.y + 5 * self.erase_button_rect.height // 6 - text.get_height() // 2 + 3))

        # Restart Text
        text = self.button_font2.render("RESTART", True, Colors.White)
        self.window.blit(text, (self.restart_button_rect.x + self.restart_button_rect.width//2 - text.get_width()//2,
                                self.restart_button_rect.y + self.restart_button_rect.height//2 - text.get_height()//2 + 2))

        # Newgame Text
        text = self.button_font2.render("NEW GAME", True, Colors.White)
        self.window.blit(text, (self.newgame_button_rect.x + self.newgame_button_rect.width // 2 - text.get_width() // 2,
                                self.newgame_button_rect.y + self.newgame_button_rect.height // 2 - text.get_height() // 2 + 2))

        # Progress Bar
        pygame.draw.rect(self.window, Colors.Black, self.progress_bar_rect, 2)
        pygame.draw.line(self.window, Colors.Gainsboro, (self.progress_bar_rect.x + 2, self.progress_bar_rect.y + 3),
                         (self.progress_bar_rect.x + self.progress_bar_rect.width - 2,
                          self.progress_bar_rect.y + 3), 1)
        pygame.draw.line(self.window, Colors.Gainsboro, (self.progress_bar_rect.x + 2, self.progress_bar_rect.y - 3 + 25),
                         (self.progress_bar_rect.x + self.progress_bar_rect.width - 2,
                          self.progress_bar_rect.y + 25 - 3), 1)
        self.current_progress = self.current_progress + (self.puzzle.get_percentage_completion() - self.current_progress)/25
        pygame.draw.rect(self.window, Colors.Azure, (self.progress_bar_rect.x + 4, self.progress_bar_rect.y + 5,
                                                     int(self.current_progress*(self.progress_bar_rect.width-6)) // 100, 25 - 8))
        text = self.small_font.render("COMPLETION: {0}%".format(trunc(self.puzzle.get_percentage_completion())),
                                      True, Colors.Azure)
        self.window.blit(text, (self.progress_bar_rect.x,
                                self.progress_bar_rect.y + self.progress_bar_rect.height + 5))

        if self.alert_timer > 0:
            text = self.small_font.render("NO CELL SELECTED!", True, Colors.ImperialRed)
            self.window.blit(text, (self.progress_bar_rect.x + self.progress_bar_rect.width - text.get_width(),
                                    self.progress_bar_rect.y + self.progress_bar_rect.height + 5))
            self.alert_timer -= 5

        # Timer
        if not self.start_time == 0:
            text = self.timer_font.render("TIME ELAPSED:  {3}:{2}:{1}:{0}".format(str(int((self.play_time * 100) % 100)).zfill(2),
                                                                                  str(int(self.play_time) % 60).zfill(2),
                                                                                  str(int(self.play_time) // 60).zfill(2),
                                                                                  str(int(self.play_time) // 3600).zfill(2)),
                                          True, Colors.Azure)
            # Decrement bonus
            self.current_bonus = (self.bonus[self.difficulty]) - ((int(self.play_time * 100) % 100) * 0.2)
        else:
            text = self.timer_font.render("TIME ELAPSED:  00:00:00:00", True, Colors.Azure)
            self.current_bonus = self.bonus[self.difficulty]
            self.error_count = 0
            self.error_deduction = 0

        self.window.blit(text, (self.pause_toggle_rect.x - 10 * text.get_width() // 9,
                                self.pause_toggle_rect.y + self.pause_toggle_rect.height // 2 - text.get_height() // 2))

        # Score
        self.score = int(self.puzzle.get_percentage_completion() * self.diff_points[self.difficulty] // 100)
        text = self.small_font.render(f"SCORE: {self.score}", True, Colors.Black)
        self.window.blit(text, (self.grid.x,
                                self.grid.y - text.get_height() - 2))

        # Errors
        text = self.small_font.render(f"ERROR COUNT: {self.error_count}", True, Colors.Black)
        self.window.blit(text, (self.grid.x + self.grid.width - text.get_width(),
                                self.grid.y - text.get_height() - 2))

        # Go to score screen if finished
        if round(self.current_progress) == 100:
            self.state = State.Scores

    def _draw_paused(self):
        """
        Handles all the drawing activites in the Paused State
        :return: None
        """
        self.window.blit(self.sudoku_bg, (0, 0))
        pygame.draw.rect(self.window, Colors.White, self.grid)
        pygame.draw.rect(self.window, Colors.White, self.number_input_buttons_rect)
        pygame.draw.rect(self.window, Colors.White, self.progress_bar_rect)
        pygame.draw.rect(self.window, Colors.White, (self.undo_button_rect.x, self.undo_button_rect.y,
                                                     self.number_input_buttons_rect.width, self.number_input_buttons_rect.height))

        self.pause_time = time.time() - self.pause_start_time
        # Drawing an empty grid for preventing player from watching it when paused
        for i in range(10):
            pygame.draw.line(self.window, Colors.Black,
                             (self.GRID_PADDING[0] + (i * self.CELL_SIZE), self.GRID_PADDING[1]),
                             (self.GRID_PADDING[0] + (i * self.CELL_SIZE), self.GRID_PADDING[1] + (9 * self.CELL_SIZE)),
                             (i % 3 == 0) + 1)
            pygame.draw.line(self.window, Colors.Black,
                             (self.GRID_PADDING[0], self.GRID_PADDING[1] + (i * self.CELL_SIZE)),
                             (self.GRID_PADDING[0] + (9 * self.CELL_SIZE), self.GRID_PADDING[1] + (i * self.CELL_SIZE)),
                             (i % 3 == 0) + 1)

        # Big play button in the center of the grid
        self.window.blit(self.big_play_button, (self.GRID_PADDING[0] + 9*self.CELL_SIZE//2 - 37,
                                                self.GRID_PADDING[1] + 9*self.CELL_SIZE//2 - 37))

        # Small play button at the top-left
        self.window.blit(self.small_play_button[self.pause_toggle_rect.collidepoint(pygame.mouse.get_pos())],
                         (self.pause_toggle_rect.x, self.pause_toggle_rect.y))

        # Drawing the buttons
        if self.current_highlighted_number:
            pygame.draw.rect(self.window, Colors.LightGray, self.current_highlighted_number)
        pygame.draw.rect(self.window, Colors.Black, self.number_input_buttons_rect, 1)
        for i in range(3):
            pygame.draw.line(self.window, Colors.Black,
                             (self.number_input_buttons_rect.x + i * self.number_input_buttons_rect.width // 3,
                              self.number_input_buttons_rect.y),
                             (self.number_input_buttons_rect.x + i * self.number_input_buttons_rect.width // 3,
                              self.number_input_buttons_rect.y + self.number_input_buttons_rect.height))
            pygame.draw.line(self.window, Colors.Black,
                             (self.number_input_buttons_rect.x,
                              self.number_input_buttons_rect.y + i * self.number_input_buttons_rect.width // 3),
                             (self.number_input_buttons_rect.x + self.number_input_buttons_rect.width,
                              self.number_input_buttons_rect.y + i * self.number_input_buttons_rect.width // 3))

        if self.current_highlighted_button:
            pygame.draw.rect(self.window, Colors.LightGray, self.current_highlighted_button)
        # Undo button
        self.window.blit(self.undo_button, (self.number_input_buttons_rect.x,
                                            self.number_input_buttons_rect.y + self.number_input_buttons_rect.height))
        pygame.draw.rect(self.window, Colors.Black, self.undo_button_rect, 1)
        # Redo Button
        self.window.blit(self.redo_button, (self.number_input_buttons_rect.x + 1 + self.number_input_buttons_rect.width//2,
                                            self.number_input_buttons_rect.y + self.number_input_buttons_rect.height))
        pygame.draw.rect(self.window, Colors.Black, self.redo_button_rect, 1)

        # Mark Button
        self.window.blit(self.marking_button, (self.marking_button_rect.x, self.marking_button_rect.y))
        pygame.draw.rect(self.window, Colors.Black, self.marking_button_rect, 1)

        # Erase Button
        self.window.blit(self.erase_button, (self.erase_button_rect.x, self.erase_button_rect.y))
        pygame.draw.rect(self.window, Colors.Black, self.erase_button_rect, 1)

        # Restart Button
        pygame.draw.rect(self.window, Colors.Azure, self.restart_button_rect)
        pygame.draw.rect(self.window, Colors.IndigoDye, self.restart_button_rect, 1)

        # New Game Button
        pygame.draw.rect(self.window, Colors.ImperialRed, self.newgame_button_rect)
        pygame.draw.rect(self.window, Colors.Black, self.newgame_button_rect, 1)

        # Drawing numbers on the buttons
        for i in range(3):
            for j in range(3):
                number = self.number_font.render(str(3 * i + j + 1), True, Colors.Black)
                self.window.blit(number,
                                 ((self.number_input_buttons_rect.x + (2 * j + 1) * self.number_input_buttons_rect.width // 6 -
                                   number.get_width() // 2),
                                  (self.number_input_buttons_rect.y + (2 * i + 1) * self.number_input_buttons_rect.width // 6 -
                                   number.get_height() // 3)))

        # Undo text
        text = self.button_font.render("UNDO", True, Colors.Black)
        self.window.blit(text, (self.undo_button_rect.x + self.undo_button.get_width() // 2 - text.get_width() // 2,
                                self.undo_button_rect.y + 5 * self.undo_button.get_height() // 6 - text.get_height() // 2 + 3))
        # Redo text
        text = self.button_font.render("REDO", True, Colors.Black)
        self.window.blit(text, (self.redo_button_rect.x + 2 + self.redo_button.get_width() // 2 - text.get_width() // 2,
                                self.redo_button_rect.y + 5 * self.undo_button.get_height() // 6 - text.get_height() // 2 + 3))

        # Mark text
        text = self.button_font.render("MARK", True, Colors.Black)
        self.window.blit(text, (self.marking_button_rect.x + self.marking_button_rect.width // 2 - text.get_width() // 2,
                                self.marking_button_rect.y + 5 * self.marking_button_rect.height // 6 - text.get_height() // 2 + 3))
        if self.puzzle.is_marking:
            text = self.small_font.render("ON", True, Colors.White)
            pygame.draw.ellipse(self.window, Colors.Azure, (self.marking_button_rect.x + 84 - text.get_width(),
                                                            self.marking_button_rect.y + 48 - text.get_height(),
                                                            2 * text.get_width(), 2 * text.get_height()))
            self.window.blit(text, (self.marking_button_rect.x + 84 - text.get_width() // 2,
                                    self.marking_button_rect.y + 48 - text.get_height() // 2))
        else:
            text = self.small_font.render("OFF", True, Colors.Black)
            pygame.draw.ellipse(self.window, Colors.Gainsboro, (self.marking_button_rect.x + 84 - text.get_width(),
                                                                self.marking_button_rect.y + 48 - text.get_height(),
                                                                2 * text.get_width(), 2 * text.get_height()))
            self.window.blit(text, (self.marking_button_rect.x + 84 - text.get_width() // 2,
                                    self.marking_button_rect.y + 48 - text.get_height() // 2))

        # Erase text
        text = self.button_font.render("ERASE", True, Colors.Black)
        self.window.blit(text, (self.erase_button_rect.x + 2 + self.erase_button_rect.width // 2 - text.get_width() // 2,
                                self.erase_button_rect.y + 5 * self.erase_button_rect.height // 6 - text.get_height() // 2 + 3))

        # Restart Text
        text = self.button_font2.render("RESTART", True, Colors.White)
        self.window.blit(text, (self.restart_button_rect.x + self.restart_button_rect.width//2 - text.get_width()//2,
                                self.restart_button_rect.y + self.restart_button_rect.height//2 - text.get_height()//2 + 2))

        # Newgame Text
        text = self.button_font2.render("NEW GAME", True, Colors.White)
        self.window.blit(text, (self.newgame_button_rect.x + self.newgame_button_rect.width // 2 - text.get_width() // 2,
                                self.newgame_button_rect.y + self.newgame_button_rect.height // 2 - text.get_height() // 2 + 2))

        # Progress Bar
        pygame.draw.rect(self.window, Colors.Black, self.progress_bar_rect, 2)
        pygame.draw.line(self.window, Colors.Gainsboro, (self.progress_bar_rect.x + 2, self.progress_bar_rect.y + 3),
                         (self.progress_bar_rect.x + self.progress_bar_rect.width - 2,
                          self.progress_bar_rect.y + 3), 1)
        pygame.draw.line(self.window, Colors.Gainsboro, (self.progress_bar_rect.x + 2, self.progress_bar_rect.y - 3 + 25),
                         (self.progress_bar_rect.x + self.progress_bar_rect.width - 2,
                          self.progress_bar_rect.y + 25 - 3), 1)
        self.current_progress = self.current_progress + (self.puzzle.get_percentage_completion() - self.current_progress) / 100
        pygame.draw.rect(self.window, Colors.Azure, (self.progress_bar_rect.x + 4, self.progress_bar_rect.y + 5,
                                                     int(self.current_progress * (self.progress_bar_rect.width - 6)) // 100, 25 - 8))
        text = self.small_font.render("COMPLETION: {0}%".format(trunc(self.puzzle.get_percentage_completion())),
                                      True, Colors.Azure)
        self.window.blit(text, (self.progress_bar_rect.x,
                                self.progress_bar_rect.y + self.progress_bar_rect.height + 5))

        # Timer
        if not self.not_ticking:
            text = self.timer_font.render("TIME ELAPSED:  {3}:{2}:{1}:{0}".format(str(int((self.play_time * 100) % 100)).zfill(2),
                                                                                  str(int(self.play_time) % 60).zfill(2),
                                                                                  str(int(self.play_time) // 60).zfill(2),
                                                                                  str(int(self.play_time) // 3600).zfill(2)),
                                          True, Colors.Azure)
        else:
            text = self.timer_font.render("TIME ELAPSED:  00:00:00:00", True, Colors.Azure)
        self.window.blit(text, (self.pause_toggle_rect.x - 10 * text.get_width() // 9,
                                self.pause_toggle_rect.y + self.pause_toggle_rect.height // 2 - text.get_height() // 2))

        # Paused Message
        text = self.small_font.render("GAME PAUSED!", True, Colors.ImperialRed)
        self.window.blit(text, (self.progress_bar_rect.x + self.progress_bar_rect.width - text.get_width(),
                                self.progress_bar_rect.y + self.progress_bar_rect.height + 5))

        # Score
        self.score = int(self.puzzle.get_percentage_completion() * 2500 // 100)
        text = self.small_font.render(f"SCORE: {self.score}", True, Colors.Black)
        self.window.blit(text, (self.grid.x,
                                self.grid.y - text.get_height() - 2))

    def _draw_scores(self):
        """
        Handles all the drawing activites in the Scores state
        :return: None
        """
        self.window.blit(self.sudoku_bg, (0, 0))
        total_score = self.score + self.current_bonus - self.error_deduction

        text = self.heading_font.render("CONGRATULATIONS! PUZZLE COMPLETED!!", True, Colors.IndigoDye)
        self.window.blit(text, (self.WIDTH // 2 - text.get_width() // 2 - 2, self.HEIGHT // 8 - text.get_height() // 2 + 2))
        text = self.heading_font.render("CONGRATULATIONS! PUZZLE COMPLETED!!", True, Colors.Azure)
        self.window.blit(text, (self.WIDTH//2 - text.get_width()//2, self.HEIGHT//8 - text.get_height()//2))

        text = self.button_font2.render("COMPLETION TIME :  {3}:{2}:{1}:{0}".format(str(int((self.play_time * 100) % 100)).zfill(2),
                                                                                    str(int(self.play_time) % 60).zfill(2),
                                                                                    str(int(self.play_time) // 60).zfill(2),
                                                                                    str(int(self.play_time) // 3600).zfill(2)),
                                        True, Colors.Black)
        self.window.blit(text, (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2 - 5 * text.get_height() // 2 - 2*text.get_height()))

        # Particulars
        text = self.button_font2.render("COMPLETION SCORE :", True, Colors.Black)
        self.window.blit(text, (self.WIDTH//5, self.HEIGHT//2 - 3*text.get_height() // 2 - text.get_height()))
        text = self.button_font2.render("BONUS SCORE :", True, Colors.Black)
        self.window.blit(text, (self.WIDTH // 5, self.HEIGHT // 2 - text.get_height() // 2 - text.get_height()))
        text = self.button_font2.render("ERRORS :", True, Colors.Black)
        self.window.blit(text, (self.WIDTH // 5, self.HEIGHT // 2 + text.get_height() // 2 - text.get_height()))

        pygame.draw.line(self.window, Colors.Black, (self.WIDTH//5, self.HEIGHT//2 + text.get_height()),
                         (4*self.WIDTH//5, self.HEIGHT//2 + text.get_height()), 2)

        text = self.button_font2.render("TOTAL SCORE :", True, Colors.ImperialRed)
        self.window.blit(text, (self.WIDTH // 5, self.HEIGHT // 2 + 2*text.get_height()))

        # Values
        self.current_bonus = max(0.0, self.current_bonus)
        text = self.button_font2.render("+ %.2f" % self.score, True, Colors.Black)
        self.window.blit(text, (4 * self.WIDTH // 5 - text.get_width(), self.HEIGHT // 2 - 3 * text.get_height() // 2 - text.get_height()))
        text = self.button_font2.render("+ %.2f" % self.current_bonus, True, Colors.Black)
        self.window.blit(text, (4 * self.WIDTH // 5 - text.get_width(), self.HEIGHT // 2 - text.get_height() // 2 - text.get_height()))
        text = self.button_font2.render("- %.2f" % self.error_deduction, True, Colors.Black)
        self.window.blit(text, (4 * self.WIDTH // 5 - text.get_width(), self.HEIGHT // 2 + text.get_height() // 2 - text.get_height()))

        text = self.button_font2.render("%.2f" % total_score, True, Colors.ImperialRed)
        self.window.blit(text, (4 * self.WIDTH // 5 - text.get_width(), self.HEIGHT // 2 + 2 * text.get_height()))

        # Buttons
        if self.home_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.window, Colors.BabyBlue, self.home_button)
        else:
            pygame.draw.rect(self.window, Colors.Azure, self.home_button)
        pygame.draw.rect(self.window, Colors.Black, self.home_button, 2)
        text = self.button_font2.render("HOME", True, Colors.White)
        self.window.blit(text, (self.home_button.x + self.home_button.width // 2 - text.get_width() // 2,
                                self.home_button.y + self.home_button.height // 2 - text.get_height() // 2))

        if self.exit_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.window, Colors.LightCoral, self.exit_button)
        else:
            pygame.draw.rect(self.window, Colors.ImperialRed, self.exit_button)
        pygame.draw.rect(self.window, Colors.Black, self.exit_button, 2)
        text = self.button_font2.render("EXIT", True, Colors.White)
        self.window.blit(text, (self.exit_button.x + self.exit_button.width // 2 - text.get_width() // 2,
                                self.exit_button.y + self.exit_button.height // 2 - text.get_height() // 2))

    def _draw(self):
        """
        Handles all the master drawing states
        :return: None
        """
        running = True

        while running:
            self.window.fill(Colors.White)
            running = self._handle_events()

            # Handling states
            self._update_state_function()
            self.state_function()

            # Update the frame
            pygame.display.update()

        pygame.quit()

Game()
