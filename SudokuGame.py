"""
This file consists the entirety of the sudoku game itself
"""
# Handle imports
import pygame
from Sudoku import Sudoku
from enum import Enum


# Setting up state enums
class State(Enum):
    Intro = 0,
    Login = 1
    Playing = 2,
    Paused = 3,
    Tutorial = 4,
    HighScores = 5


class Colors:
    White = (255, 255, 255),
    Black = (0, 0, 0),
    AliceBlue = (227, 240, 255),
    BabyBlue = (140, 217, 255),
    WebLavender = (219, 226, 236),
    NeonBlue = (62, 110, 255)
    CrayolaPeriwinkle = (211, 224, 245)
    ImperialRed = (255, 10, 62)
    LightGray = (239, 245, 245)
    LightCoral = (255, 130, 134)


# The game object
class Game:
    def __init__(self):
        # PyGame Attributes
        self.window = None
        self.WIDTH = 825
        self.HEIGHT = 600
        self.GRID_PADDING = (50, 100)
        self.CELL_SIZE = 50
        self.state = State.Playing
        self.state_function = None
        self.current_highlighted_cell = None
        self.current_selected_cell = None
        self.current_highlighted_number = None
        self.current_highlighted_button = None
        self.grid = pygame.Rect(self.GRID_PADDING[0], self.GRID_PADDING[1], 9*self.CELL_SIZE, 9*self.CELL_SIZE)

        # Pygame setup
        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Sudoku Forever!")

        # Buttons
        self.small_play_button = (pygame.image.load("PlayButtonIdle.png"), pygame.image.load("PlayButtonActive.png"))
        self.big_play_button = pygame.image.load("PlayButton.png")
        self.small_pause_button = (pygame.image.load("PauseButtonIdle.png"), pygame.image.load("PauseButtonActive.png"))
        self.pause_toggle_rect = pygame.Rect(self.WIDTH - 16 - 32, 16, 32, 32)
        self.number_input_buttons_rect = pygame.Rect(2*self.GRID_PADDING[0] + 9*self.CELL_SIZE,
                                                     self.GRID_PADDING[1] + 9*self.CELL_SIZE//8,
                                                     9*self.CELL_SIZE//2, 9*self.CELL_SIZE//2)
        self.undo_button = pygame.image.load("UndoButton.png")
        self.undo_button_rect = pygame.Rect(self.number_input_buttons_rect.x,
                                            self.number_input_buttons_rect.y +
                                            self.number_input_buttons_rect.height - 1,
                                            self.undo_button.get_width() + 2, self.undo_button.get_height())
        self.redo_button = pygame.image.load("RedoButton.png")
        self.redo_button_rect = pygame.Rect(self.number_input_buttons_rect.x + 1 +
                                            self.number_input_buttons_rect.width//2,
                                            self.number_input_buttons_rect.y +
                                            self.number_input_buttons_rect.height - 1,
                                            self.redo_button.get_width(), self.redo_button.get_height())
        self.marking_button = pygame.image.load("MarkButton.png")
        self.marking_button_rect = pygame.Rect(self.undo_button_rect.x,
                                               self.undo_button_rect.y + self.undo_button_rect.height - 1,
                                               self.marking_button.get_width() + 2, self.marking_button.get_height())
        self.erase_button = pygame.image.load("EraseButton.png")
        self.erase_button_rect = pygame.Rect(self.marking_button_rect.x + self.marking_button_rect.width - 1,
                                             self.marking_button_rect.y,
                                             self.redo_button_rect.width, self.redo_button_rect.height)

        # Fonts
        self.grid_font = pygame.font.SysFont("calibri", (3*self.CELL_SIZE)//5)
        self.number_font = pygame.font.SysFont("calibri", self.number_input_buttons_rect.width//5)
        self.button_font = pygame.font.SysFont("calibri", self.undo_button.get_height()//4)
        self.small_font = pygame.font.SysFont("calibri", 14)

        # Game attributes
        self.puzzle = Sudoku()
        self.puzzle.initialize_puzzle(25)
        self.difficulty = None

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
        elif self.state is State.Tutorial:
            self.state_function = self._draw_tutorial
        elif self.state is State.HighScores:
            self.state_function = self._draw_highscores

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

            # TODO: Intro Events

            # TODO: Login Events

            # Playing Events
            if self.state == State.Playing:
                # Keyboard inputs
                if event.type == pygame.KEYDOWN:
                    # Undo when ctrl+z is pressed
                    if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.puzzle.undo()
                    # Redo when ctrl+r is pressed
                    if event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.puzzle.redo()

                # Check if the mouse is one the grid
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
                            self.puzzle.insert((self.current_selected_cell[0] - self.GRID_PADDING[0])//self.CELL_SIZE,
                                               (self.current_selected_cell[1] - self.GRID_PADDING[1])//self.CELL_SIZE,
                                               number)
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

                # Otherwise just remove the highlighted cell
                else:
                    self.current_highlighted_cell = None
                    self.current_highlighted_number = None
                    self.current_highlighted_button = None

            # Paused Events
            elif self.state == State.Paused:
                # Un-pause methods
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.grid.collidepoint(event.pos) \
                            or self.pause_toggle_rect.collidepoint(event.pos)\
                            or self.number_input_buttons_rect.collidepoint(event.pos)\
                            or self.undo_button_rect.collidepoint(event.pos)\
                            or self.redo_button_rect.collidepoint(event.pos)\
                            or self.marking_button_rect.collidepoint(event.pos):
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

                else:
                    self.current_highlighted_number = None
                    self.current_highlighted_button = None

            # TODO: HighScore Events

            # TODO: Tutorial Events

        return True

    def _draw_intro(self):
        # TODO: Implement drawing intro
        pass

    def _draw_login(self):
        # TODO: Implement drawing login
        pass

    def _draw_playing(self):
        # Draw the current cell that the mouse is hovering over
        if self.current_highlighted_cell:
            pygame.draw.rect(self.window, Colors.AliceBlue, self.current_highlighted_cell)

        # Draw the currently selected cell and its corresponding rows, columns, boxes and boxes with the same digit
        if self.current_selected_cell:
            x, y = self.current_selected_cell[:2]
            pygame.draw.rect(self.window, Colors.WebLavender,
                             (self.GRID_PADDING[0], y, 9*self.CELL_SIZE, self.CELL_SIZE))
            pygame.draw.rect(self.window, Colors.WebLavender,
                             (x, self.GRID_PADDING[1], self.CELL_SIZE, 9*self.CELL_SIZE))
            pygame.draw.rect(self.window, Colors.WebLavender,
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
                            num = self.grid_font.render(str(self.puzzle.current_sudoku_puzzle[x][y]), True, Colors.NeonBlue)
                    else:
                        # Display block number in Black
                        num = self.grid_font.render(str(self.puzzle.current_sudoku_puzzle[x][y]), True, Colors.Black)
                    # Draw the number with the appropriate color
                    self.window.blit(num,
                                     (self.GRID_PADDING[0] + self.CELL_SIZE//2 + x*self.CELL_SIZE - num.get_width()//2,
                                      self.GRID_PADDING[1] + self.CELL_SIZE//2 + y*self.CELL_SIZE - num.get_height()//3))

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
            pygame.draw.ellipse(self.window, Colors.NeonBlue, (self.marking_button_rect.x + 84 - text.get_width(),
                                                               self.marking_button_rect.y + 48 - text.get_height(),
                                                               2 * text.get_width(), 2 * text.get_height()))
            self.window.blit(text, (self.marking_button_rect.x + 84 - text.get_width() // 2,
                                    self.marking_button_rect.y + 48 - text.get_height() // 2))
        else:
            text = self.small_font.render("OFF", True, Colors.Black)
            pygame.draw.ellipse(self.window, Colors.WebLavender, (self.marking_button_rect.x + 84 - text.get_width(),
                                                                  self.marking_button_rect.y + 48 - text.get_height(),
                                                                  2 * text.get_width(), 2 * text.get_height()))
            self.window.blit(text, (self.marking_button_rect.x + 84 - text.get_width() // 2,
                                    self.marking_button_rect.y + 48 - text.get_height() // 2))

        # Erase text
        text = self.button_font.render("ERASE", True, Colors.Black)
        self.window.blit(text, (self.erase_button_rect.x + 2 + self.erase_button_rect.width // 2 - text.get_width() // 2,
                                self.erase_button_rect.y + 5 * self.erase_button_rect.height // 6 - text.get_height() // 2 + 3))

    def _draw_paused(self):
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
            pygame.draw.ellipse(self.window, Colors.NeonBlue, (self.marking_button_rect.x + 84 - text.get_width(),
                                                               self.marking_button_rect.y + 48 - text.get_height(),
                                                               2 * text.get_width(), 2 * text.get_height()))
            self.window.blit(text, (self.marking_button_rect.x + 84 - text.get_width() // 2,
                                    self.marking_button_rect.y + 48 - text.get_height() // 2))
        else:
            text = self.small_font.render("OFF", True, Colors.Black)
            pygame.draw.ellipse(self.window, Colors.WebLavender, (self.marking_button_rect.x + 84 - text.get_width(),
                                                                  self.marking_button_rect.y + 48 - text.get_height(),
                                                                  2 * text.get_width(), 2 * text.get_height()))
            self.window.blit(text, (self.marking_button_rect.x + 84 - text.get_width() // 2,
                                    self.marking_button_rect.y + 48 - text.get_height() // 2))

        # Erase text
        text = self.button_font.render("ERASE", True, Colors.Black)
        self.window.blit(text, (self.erase_button_rect.x + 2 + self.erase_button_rect.width // 2 - text.get_width() // 2,
                                self.erase_button_rect.y + 5 * self.erase_button_rect.height // 6 - text.get_height() // 2 + 3))

    def _draw_tutorial(self):
        # TODO: Implement drawing tutorial
        pass

    def _draw_highscores(self):
        # TODO: Implement drawing HighScores
        pass

    def _draw(self):
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


# TODO: 1.Custom Buttons
# TODO: 2.Menu Options
# TODO: 3.State Machine
# TODO: 4.GamePlay Interface
# TODO: 5.Pausing mechanic
# TODO: 6.Handling input from user
# TODO: 7.HighScore and LeaderBoard
# TODO: 8.Difficulty Selection
# TODO: 9.Tutorial section

Game()
