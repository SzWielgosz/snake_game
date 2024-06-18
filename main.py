# Icons: https://www.flaticon.com/authors/freepik
from tkinter import *
import random
import time
import numpy as np
from PIL import ImageTk,Image

# Define useful parameters
size_of_board = 1000
rows = 20
cols = 20
DELAY = 100
snake_initial_length = 3
symbol_size = (size_of_board / 3 - size_of_board / 8) / 2
symbol_thickness = 2
RED_COLOR = "#EE4035"
BLUE_COLOR = "#0492CF"
Green_color = "#7BC043"
BLUE_COLOR_LIGHT = '#67B0CF'
RED_COLOR_LIGHT = '#EE7E77'
BLACK_COLOR = '#000000'
GREY_COLOR = '#808080'


class SnakeAndApple:
    # ------------------------------------------------------------------
    # Initialization Functions:
    # ------------------------------------------------------------------
    def __init__(self):
        self.window = Tk()
        self.window.title("Snake-and-Apple")
        self.canvas = Canvas(self.window, width=size_of_board, height=size_of_board)
        self.canvas.pack()
        # Input from user in form of clicks and keyboard
        self.window.bind("<Key>", self.key_input)
        self.window.bind("<Button-1>", self.mouse_input)
        self.enemy_shapes = ["dot", "snake", "cross", "pyramid"]
        self.armor_place_timer = 60
        self.armor_placed = False
        self.play_again()
        self.begin = False

    def initialize_board(self):
        self.board = []
        self.apple_obj = []
        self.armor_obj = []
        self.debuff_obj = []
        self.old_apple_cell = []

        for i in range(rows):
            for j in range(cols):
                self.board.append((i, j))

        for i in range(rows):
            self.canvas.create_line(
                i * size_of_board / rows, 0, i * size_of_board / rows, size_of_board,
            )

        for i in range(cols):
            self.canvas.create_line(
                0, i * size_of_board / cols, size_of_board, i * size_of_board / cols,
            )

    def initialize_snake(self):
        self.snake = []
        self.crashed = False
        self.has_armor = False
        self.snake_heading = "Right"
        self.last_key = self.snake_heading
        self.forbidden_actions = {}
        self.forbidden_actions["Right"] = "Left"
        self.forbidden_actions["Left"] = "Right"
        self.forbidden_actions["Up"] = "Down"
        self.forbidden_actions["Down"] = "Up"
        self.snake_objects = []
        for i in range(snake_initial_length):
            self.snake.append((i, 0))

    def create_enemy_shape(self, shape):
        enemy_shape = []
        if shape in self.enemy_shapes:
            match shape:
                case "dot":
                    enemy_shape = [(rows - 1, cols - 1)]
                case "snake":
                    enemy_shape = [(i, cols - 1) for i in range(0, rows)]
                case "cross":
                    enemy_shape = [(rows - 2, cols - 3), (rows - 3, cols - 2), (rows - 2, cols - 1), (rows - 1, cols - 2), (rows - 2, cols - 2)]
                case "pyramid":
                    enemy_shape = [(rows - 1, cols - 1), (rows - 2, cols - 1), (rows - 3, cols - 1), (rows - 4, cols - 1), (rows - 5, cols - 1), (rows - 2, cols - 2), (rows - 3, cols - 2), (rows - 4, cols - 2), (rows - 3, cols - 3)]
        return enemy_shape
    
    def initialize_enemy(self):
        self.enemy_shape = "pyramid"
        self.enemy = self.create_enemy_shape(self.enemy_shape)
        self.enemy_objects = []
        self.enemy_delay = 0
        self.enemy_stunned = False
        self.stun_duration = 30

    def delete_enemy_objects(self, shape):
        if shape in self.enemy_shapes:
            match shape:
                case "dot":
                    self.canvas.delete(self.enemy_objects.pop(0))
                case "snake":
                    for i in self.enemy:
                        self.canvas.delete(self.enemy_objects.pop(0))
                case "cross":
                    for i in self.enemy:
                        self.canvas.delete(self.enemy_objects.pop(0))
                case "pyramid":
                    for i in self.enemy:
                        self.canvas.delete(self.enemy_objects.pop(0))
    

    def play_again(self):
        self.canvas.delete("all")
        self.armor_placed = False
        self.armor_place_timer = 60
        self.initialize_board()
        self.initialize_snake()
        self.initialize_enemy()
        self.place_apple()
        self.display_snake(mode="complete")
        self.display_enemy()
        self.begin_time = time.time()


    def mainloop(self):
        while True:
            self.window.update()
            if self.begin:
                if not self.crashed:
                    self.window.after(DELAY, self.update())
                else:
                    self.begin = False
                    self.window.after(DELAY, self.display_gameover())

    # ------------------------------------------------------------------
    # Drawing Functions:
    # The modules required to draw required game based object on canvas
    # ------------------------------------------------------------------
    def display_gameover(self):
        score = len(self.snake)
        self.canvas.delete("all")
        score_text = "Score: \n"

        # put gif image on canvas
        # pic's upper left corner (NW) on the canvas is at x=50 y=10

        self.canvas.create_text(
            size_of_board / 2,
            3 * size_of_board / 8,
            font="cmr 40 bold",
            fill=Green_color,
            text=score_text,
        )
        score_text = str(score)
        self.canvas.create_text(
            size_of_board / 2,
            1 * size_of_board / 2,
            font="cmr 50 bold",
            fill=BLUE_COLOR,
            text=score_text,
        )
        time_spent = str(np.round(time.time() - self.begin_time, 1)) + 'sec'
        self.canvas.create_text(
            size_of_board / 2,
            3 * size_of_board / 4,
            font="cmr 20 bold",
            fill=BLUE_COLOR,
            text=time_spent,
        )
        score_text = "Click to play again \n"
        self.canvas.create_text(
            size_of_board / 2,
            15 * size_of_board / 16,
            font="cmr 20 bold",
            fill="gray",
            text=score_text,
        )

    def place_apple(self):
        # Place apple randomly anywhere except at the cells occupied by snake
        unoccupied_cels = set(self.board) - set(self.snake) - set(self.enemy)
        self.apple_cell = random.choice(list(unoccupied_cels))
        row_h = int(size_of_board / rows)
        col_w = int(size_of_board / cols)
        x1 = self.apple_cell[0] * row_h
        y1 = self.apple_cell[1] * col_w
        x2 = x1 + row_h
        y2 = y1 + col_w
        self.apple_obj = self.canvas.create_rectangle(
            x1, y1, x2, y2, fill=RED_COLOR_LIGHT, outline=BLUE_COLOR,
        )


    def place_armor(self):
        unoccupied_cells = set(self.board) - set(self.snake) - set(self.enemy) - set(self.apple_cell)
        self.armor_cell = random.choice(list(unoccupied_cells))
        row_h = int(size_of_board / rows)
        col_w = int(size_of_board / cols)
        x1 = self.armor_cell[0] * row_h
        y1 = self.armor_cell[1] * col_w
        x2 = x1 + row_h
        y2 = y1 + col_w
        self.armor_obj = self.canvas.create_rectangle(
            x1, y1, x2, y2, fill=GREY_COLOR, outline=BLACK_COLOR,
        )

    
    def display_enemy(self):
        for i, cell in enumerate(self.enemy):
            enemy_cell = cell
            row_h = int(size_of_board / rows)
            col_w = int(size_of_board / cols)
            x1 = enemy_cell[0] * row_h
            y1 = enemy_cell[1] * col_w
            x2 = x1 + row_h
            y2 = y1 + col_w
            
            if len(self.enemy_objects) == len(self.enemy):
                # Move enemy objects to new position
                self.canvas.coords(self.enemy_objects[i], x1, y1, x2, y2)
                self.canvas.tag_raise(self.enemy_objects[i]) # If two rectangles overlap, display this one on the screen
            else:
                # If there's no enemy objects, create them
                rectangle = self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill=BLACK_COLOR, outline=BLACK_COLOR
                    )
                self.enemy_objects.append(
                    rectangle
                )


    def display_snake(self, mode=""):
        if mode == "complete":
            # Draw the whole snake
            for i, cell in enumerate(self.snake):
                self.draw_snake_segment(i, cell)
        else:
            # Update the whole snake
            if self.has_armor:
                self.change_color(color=GREY_COLOR)

            for i, cell in enumerate(self.snake):
                if i == len(self.snake) - 1:
                    # For the head of the snake
                    self.move_snake_segment(i, cell)
                else:
                    # For the rest of the snake's body
                    self.move_snake_segment(i, self.snake[i])
                
            # Check if the snake ate the apple
            head = self.snake[-1]
            if head == self.old_apple_cell:
                # Add a new segment to the snake
                self.snake.insert(0, self.old_apple_cell)
                self.draw_snake_segment(0, self.old_apple_cell)
                self.old_apple_cell = []  # Clear apple position

        self.window.update()  # Refresh the window


    def draw_snake_segment(self, index, cell):
        row_h = int(size_of_board / rows)
        col_w = int(size_of_board / cols)
        x1 = cell[0] * row_h
        y1 = cell[1] * col_w
        x2 = x1 + row_h
        y2 = y1 + col_w
        
        segment_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=BLUE_COLOR, outline=RED_COLOR)
        
        self.snake_objects.insert(index, segment_id)

    
    def change_color(self, color):
        for i in self.snake_objects:
            self.canvas.itemconfig(i, fill=color)
    

    def move_snake_segment(self, index, cell):
        row_h = int(size_of_board / rows)
        col_w = int(size_of_board / cols)
        x1 = cell[0] * row_h
        y1 = cell[1] * col_w
        x2 = x1 + row_h
        y2 = y1 + col_w
        
        if self.snake_objects:
            segment_id = self.snake_objects.pop(index)
            self.canvas.coords(segment_id, x1, y1, x2, y2)
            self.snake_objects.insert(index, segment_id)



    # ------------------------------------------------------------------
    # Logical Functions:
    # The modules required to carry out game logic
    # ------------------------------------------------------------------
    def update_snake(self, key):
        # Check if it hit the wall or its own body
        tail = self.snake[0]
        head = self.snake[-1]

        if tail != self.old_apple_cell:
            self.snake.pop(0)

        if self.armor_placed:
            if head == self.armor_cell:
                self.canvas.delete(self.armor_obj)
                self.has_armor = True
                self.armor_placed = False

        match key:
            case "Left":
                self.snake.append((head[0] - 1, head[1]))

            case "Right":
                self.snake.append((head[0] + 1, head[1]))

            case "Up":
                self.snake.append((head[0], head[1] - 1))

            case "Down":
                self.snake.append((head[0], head[1] + 1))

        head = self.snake[-1]

        if (
                head[0] > cols - 1
                or head[0] < 0
                or head[1] > rows - 1
                or head[1] < 0
                or len(set(self.snake)) != len(self.snake)
        ):
            # Hit the wall / Hit on body
            self.crashed = True

            # Hit on enemy
        if any(head == enemy_pos for enemy_pos in self.enemy):
            if self.has_armor:
                self.enemy_stunned = True
                self.has_armor = False
                self.change_color(color=BLUE_COLOR)
            else:
                if not self.enemy_stunned:
                    self.crashed = True

        elif self.apple_cell == head:
            # Got the apple
            self.old_apple_cell = self.apple_cell
            self.canvas.delete(self.apple_obj)
            self.place_apple()
            self.display_snake()

        else:
            self.snake_heading = key
            self.display_snake()


    def update_enemy(self):
        if self.enemy_stunned:
            if self.stun_duration != 0:
                self.stun_duration -= 1
                return
            else:
                self.enemy_stunned = False
                self.stun_duration = 30

        if self.enemy_delay < 1:
            self.enemy_delay += 1

        else:
            if self.enemy_shape == "cross" or self.enemy_shape == "pyramid":
                enemy_head = np.array(self.enemy[-1])
                snake_head = np.array(self.snake[-1])
                diff = enemy_head - snake_head
                diff = (int(diff[0]), int(diff[1]))
                if np.abs(diff[0]) > np.abs(diff[1]):
                    if diff[0] > 0:
                        direction = np.array([-1, 0]) # Left
                    else:
                        direction = np.array([1, 0]) # Right
                else:
                    if diff[1] > 0:
                        direction = np.array([0, -1]) # Top
                    else:
                        direction = np.array([0, 1]) # Down

                x = len(self.enemy)

                for i in range(x):
                    self.enemy.append(tuple(self.enemy[i] + direction))

                for i in range(x):
                    self.enemy.pop(0)
                
            else:
                enemy_head = np.array(self.enemy[-1])
                snake_head = np.array(self.snake[-1])
                diff = enemy_head - snake_head
                diff = (int(diff[0]), int(diff[1]))
                self.enemy.pop(0)
                if np.abs(diff[0]) > np.abs(diff[1]):
                    if diff[0] > 0:
                        self.enemy.append(tuple(enemy_head + np.array([-1, 0]))) # Left
                    else:
                        self.enemy.append(tuple(enemy_head + np.array([1, 0]))) # Right
                else:
                    if diff[1] > 0:
                        self.enemy.append(tuple(enemy_head + np.array([0, -1]))) # Top
                    else:
                        self.enemy.append(tuple(enemy_head + np.array([0, 1]))) # Down
            self.enemy_delay = 0
            
        self.display_enemy()


    def update(self):
        self.update_snake(self.last_key)
        self.update_enemy()
        if not self.armor_placed and not self.has_armor:
            self.armor_place_timer -= 1
            if self.armor_place_timer <= 0:
                self.place_armor()
                self.armor_placed = True
                self.armor_place_timer = 60


    def check_if_key_valid(self, key):
        valid_keys = ["Up", "Down", "Left", "Right"]
        if key in valid_keys and self.forbidden_actions[self.snake_heading] != key:
            return True
        else:
            return False

    def mouse_input(self, event):
        self.play_again()

    def key_input(self, event): 
        if not self.crashed:
            key_pressed = event.keysym
            # Check if the pressed key is a valid key
            if self.check_if_key_valid(key_pressed):
                self.begin = True
                self.last_key = key_pressed

game_instance = SnakeAndApple()
game_instance.mainloop()
