import pygame as pg
import random
import time

pg.init()

class Tetris:
    def __init__(self, window_size): # Size of each box on the board in pixels
        print("Inicializando Tetris...")
        self.board_square = window_size  
        self.window = pg.display.set_mode((window_size * 14, window_size * 20)) 
        pg.display.set_caption("Tetris")
        self.clock = pg.time.Clock()  
        pg.font.init()
        self.font = pg.font.SysFont('Comic Sans MS', window_size, bold=True)  # Text font for score and next shape display
        
        self.time = 0  
        self.starting_first_game = True  
        self.show_restart_button = False  
        self.next_shapes_list = ["", "", "", ""]  
        self.score = 0  
        self.speed = 1  
        self.selected_form = "shape_1"  
        self.shape_pos = [4, 0]  
        self.shape_matrix = [[]]  
        self.new_shape = True  
        self.last_click_status = (False, False, False)  

        # Colors in RGB format
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.gray = (150, 150, 150)
        self.purple = (171, 57, 219)
        self.blue = (23, 31, 223)
        self.light_blue = (3, 133, 223)
        self.red = (246, 51, 73)
        self.orange = (250, 123, 21)
        self.yellow = (245, 198, 42)
        self.green = (99, 209, 21)

        # Shapes for mapping, shape codes to their matrix and color
        self.shapes = {
            "shape_1": {"matrix": [[1, 1, 1, 1]], "color": self.yellow},
            "shape_2": {"matrix": [[1, 1], [1, 1]], "color": self.red},
            "shape_3": {"matrix": [[0, 1, 0], [1, 1, 1]], "color": self.purple},
            "shape_4": {"matrix": [[0, 1, 1], [1, 1, 0]], "color": self.green},
            "shape_5": {"matrix": [[1, 1, 0], [0, 1, 1]], "color": self.blue},
            "shape_6": {"matrix": [[1, 0, 0], [1, 1, 1]], "color": self.orange},
            "shape_7": {"matrix": [[0, 0, 1], [1, 1, 1]], "color": self.light_blue},
        }

        # Map representing the game board, initially empty
        self.map = [["" for _ in range(10)] for _ in range(20)]
        
        self.init_random_shapes()
        self.get_next_shape()

    def new_random_shape(self): # Generate a new random shape code (shape_1 to shape_7)
        return f"shape_{random.randint(1, 7)}"

    def add_random_shape(self): # Add a new random shape to the end of the list of upcoming shapes and shift the existing shapes to the left
        for i in range(len(self.next_shapes_list)):
            if i != 0:
                self.next_shapes_list[i - 1] = self.next_shapes_list[i]
        self.next_shapes_list[-1] = self.new_random_shape()

    def init_random_shapes(self):
        for i in range(4):
            self.next_shapes_list[i] = self.new_random_shape()

    def get_next_shape(self): # Get the next shape from the list of upcoming shapes, set it as the current shape, and prepare the next shape in the list
        self.selected_form = self.next_shapes_list[0]
        self.shape_matrix = [row[:] for row in self.shapes[self.selected_form]["matrix"]]
        # centraliza horizontalmente a peça no tabuleiro de 10 colunas
        self.shape_pos = [ (10 - len(self.shape_matrix[0])) // 2, 0 ]
        self.add_random_shape()
        self.new_shape = False

    def did_shape_collide_sideways(self): # Check if the current shape has collided with the sides of the board or with locked shapes when moving left or right
        for y in range(len(self.shape_matrix)):
            for x in range(len(self.shape_matrix[0])):
                if self.shape_matrix[y][x] == 1:
                    map_x = self.shape_pos[0] + x
                    map_y = self.shape_pos[1] + y
                    if map_x < 0 or map_x >= 10 or (map_y >= 0 and map_y < 20 and self.map[map_y][map_x] != ""):
                        return True
        return False

    def lock_shape(self): # Lock the shape in place on the board when it collides with the bottom or with other locked shapes
        shape_pos_x = self.shape_pos[0]
        shape_pos_y = self.shape_pos[1]
        for y in range(len(self.shape_matrix)):
            for x in range(len(self.shape_matrix[0])):
                if self.shape_matrix[y][x] == 1:
                    if 0 <= shape_pos_y + y < 20 and 0 <= shape_pos_x + x < 10:
                        self.map[shape_pos_y + y][shape_pos_x + x] = self.shapes[self.selected_form]["color"]
        self.remove_completed_rows()
        self.get_next_shape()

    def rotate_shape_to_the_right(self): # Rotate the shape to the right (clockwise)
        transpose_matrix = list(zip(*self.shape_matrix))
        self.shape_matrix = [list(row[::-1]) for row in transpose_matrix]

    def rotate_shape_to_the_left(self): # Rotate the shape to the left (counterclockwise)
        transpose_matrix = list(zip(*self.shape_matrix))
        self.shape_matrix = [list(row) for row in transpose_matrix[::-1]]

    def send_shape_to_end(self): # Move the shape down until it collides with something, then lock it in place
        for i in range(20):
            self.shape_pos[1] += 1
            if self.check_collision():
                self.shape_pos[1] -= 1
                self.lock_shape()
                return

    def check_collision(self): # Check if the current shape has collided with the bottom of the board or with locked shapes
        shape_pos_x = self.shape_pos[0]
        shape_pos_y = self.shape_pos[1]
        for y in range(len(self.shape_matrix)):
            for x in range(len(self.shape_matrix[0])):
                if self.shape_matrix[y][x] == 1:
                    if shape_pos_y + y >= 20:
                        return True
                    if shape_pos_y + y >= 0 and shape_pos_x + x >= 0 and shape_pos_x + x < 10:
                        if self.map[shape_pos_y + y][shape_pos_x + x] != "":
                            return True
        return False

    def move_shape(self, key): # Move the shape based on the key pressed (left, right, down, rotate)
      if key == "a" or key == "left":
        self.shape_pos[0] -= 1
        if self.did_shape_collide_sideways():
            self.shape_pos[0] += 1
      elif key == "s" or key == "down":
        self.shape_pos[1] += 1
        if self.check_collision():
            self.shape_pos[1] -= 1
            self.lock_shape()
      elif key == "d" or key == "right":
        self.shape_pos[0] += 1
        if self.did_shape_collide_sideways():
            self.shape_pos[0] -= 1
      elif key == 'q':
        self.rotate_shape_to_the_left()
      elif key == 'e':
        self.rotate_shape_to_the_right()
      elif key == "space":
        self.send_shape_to_end()

    def clear_window(self): # Clear the game window by filling it with white color
        self.window.fill(self.white)

    def game_step(self): # Move the shape down automatically based on the current speed of the game
        self.time += 1
        if self.time >= 60 / self.speed:
            self.shape_pos[1] += 1
            self.time = 0
            if self.check_collision():
                self.shape_pos[1] -= 1
                self.lock_shape()

    def game_speed(self): # Increase the game speed based on the current score, with a maximum speed limit
        self.speed = min(1 + self.score // 100, 50)

    def remove_completed_rows(self): # Check for completed rows in the board, remove them, and update the score accordingly
        completed_rows = []
        for y in range(20):
            if all(self.map[y][x] != "" for x in range(10)):
                completed_rows.append(y)
        
        if completed_rows:
            for row in completed_rows:
                del self.map[row]
                self.map.insert(0, ["" for _ in range(10)])
            self.score += len(completed_rows) * 100
            self.game_speed()

    def restart_game(self, restart=False): # Restart the game by reinitializing all variables and starting a new game, but only if it's not the first game or if the restart flag is set to True
        if self.starting_first_game == False or restart:
            self.init_random_shapes()
            self.score = 0
            self.speed = 1
            self.map = [["" for _ in range(10)] for _ in range(20)]
            self.show_restart_button = False
            self.starting_first_game = False
            self.get_next_shape()

    def draw_shapes_in_game(self): # Draw the locked shapes on the board and the current falling shape, with a border around each block for better visibility
        for y in range(20):
            for x in range(10):
                if self.map[y][x] != "":
                    color = self.map[y][x]
                    border_color = tuple(min(rgb + 50, 255) for rgb in color)
                    pg.draw.rect(self.window, color, (x * self.board_square, y * self.board_square, self.board_square, self.board_square))
                    pg.draw.rect(self.window, border_color, (x * self.board_square, y * self.board_square, self.board_square, self.board_square), 1)
        
        shape_pos_x = self.shape_pos[0]
        shape_pos_y = self.shape_pos[1]
        color = self.shapes[self.selected_form]["color"]
        border_color = tuple(min(rgb + 50, 255) for rgb in color)
        for y in range(len(self.shape_matrix)):
            for x in range(len(self.shape_matrix[0])):
                if self.shape_matrix[y][x] == 1:
                    pg.draw.rect(self.window, color, ((shape_pos_x + x) * self.board_square, (shape_pos_y + y) * self.board_square, self.board_square, self.board_square))
                    pg.draw.rect(self.window, border_color, ((shape_pos_x + x) * self.board_square, (shape_pos_y + y) * self.board_square, self.board_square, self.board_square), 1)

    def is_game_end(self): # Check if the game has ended by verifying if the current shape has collided with the top of the board or with locked shapes when it spawns
        shape_pos_x = self.shape_pos[0]
        shape_pos_y = self.shape_pos[1]
        for y in range(len(self.shape_matrix)):
            for x in range(len(self.shape_matrix[0])):
                if self.shape_matrix[y][x] == 1:
                    map_y = shape_pos_y + y
                    map_x = shape_pos_x + x
                    if map_y < 0:
                        return True
                    if 0 <= map_y < 20 and 0 <= map_x < 10:
                        if self.map[map_y][map_x] != "":
                            return True
        return False

    def mouse_has_clicked(self, input_state):
        if self.last_click_status == input_state:
            return (False, False, False)
        left_button = self.last_click_status[0] == False and input_state[0] == True
        center_button = self.last_click_status[1] == False and input_state[1] == True
        right_button = self.last_click_status[2] == False and input_state[2] == True
        return (left_button, center_button, right_button)

    def draw_next_shapes(self):
        
        preview_left = self.board_square * 10
        preview_width = self.board_square * 4

        for i, next_shape_code in enumerate(self.next_shapes_list):
            if not next_shape_code:
                continue
            shape_matrix = self.shapes[next_shape_code]["matrix"]

            
            shape_pixel_width = len(shape_matrix[0]) * self.board_square
            next_shape_x = preview_left + (preview_width - shape_pixel_width) / 2
            
            next_shape_y = self.board_square * (2 + i * 3)

            color = self.shapes[next_shape_code]["color"]
            border_color = tuple(min(rgb + 50, 255) for rgb in color)
            for y in range(len(shape_matrix)):
                for x in range(len(shape_matrix[0])):
                    if shape_matrix[y][x] == 1:
                        px = next_shape_x + (x * self.board_square)
                        py = next_shape_y + (y * self.board_square)
                        pg.draw.rect(self.window, color, (px, py, self.board_square, self.board_square))
                        pg.draw.rect(self.window, border_color, (px, py, self.board_square, self.board_square), 1)

    def text_box(self, text, x, y, width, height, background_fill): # Draw a text box with the specified text, position, size, and background fill option
        next_square_x = self.board_square * x
        next_square_y = self.board_square * y
        next_square_w = self.board_square * width
        next_square_h = self.board_square * height
        if background_fill:
            pg.draw.rect(self.window, self.gray, (next_square_x, next_square_y, next_square_w, next_square_h))
        pg.draw.rect(self.window, self.black, (next_square_x, next_square_y, next_square_w, next_square_h), 2)
        next_text = self.font.render(text, 1, self.black)
        next_text_w = next_text.get_width()
        next_text_h = next_text.get_height()
        blit_x = next_square_x + (next_square_w - next_text_w) / 2
        blit_y = next_square_y + (next_square_h - next_text_h) / 2
        self.window.blit(next_text, (blit_x, blit_y))

    def board(self):
        for y in range(20):
            for x in range(10):
                pg.draw.rect(self.window, self.gray, (x * self.board_square, y * self.board_square, self.board_square, self.board_square), 1)
        pg.draw.rect(self.window, self.black, (0, 0, self.board_square * 10, self.board_square * 20), 2)

    def draw_restart_button(self): # Draw a restart button in the center of the screen when the game ends, allowing the player to start a new game
        button_color = self.gray
        button_width = self.window.get_width() - (self.board_square * 10)
        button_height = button_width / 2
        button_x = (self.window.get_width() - button_width) / 2
        button_y = (self.window.get_height() - button_height) / 2
        pg.draw.rect(self.window, button_color, (button_x, button_y, button_width, button_height))
        pg.draw.rect(self.window, self.black, (button_x, button_y, button_width, button_height), 2)
        button_text = self.font.render("Restart", 1, self.black)
        self.window.blit(button_text, (button_x + button_width / 2 - button_text.get_width() / 2, button_y + button_height / 2 - button_text.get_height() / 2))

    def restart_button_clicked(self, mouse): # Check if the restart button has been clicked by the mouse and restart the game if it has
        if self.show_restart_button:
            button_width = self.window.get_width() - (self.board_square * 10)
            button_height = button_width / 2
            button_x = (self.window.get_width() - button_width) / 2
            button_y = (self.window.get_height() - button_height) / 2
            if (mouse["position"][0] >= button_x and mouse["position"][0] <= button_x + button_width and
                mouse["position"][1] >= button_y and mouse["position"][1] <= button_y + button_height):
                if mouse["click"][0]:
                    self.restart_game(True)

    def run(self):
        self.restart_game()
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    self.move_shape(pg.key.name(event.key))
                    if pg.key.name(event.key) == "escape":
                        running = False

            mouse_position = pg.mouse.get_pos()
            mouse_input = pg.mouse.get_pressed()
            mouse_click = self.mouse_has_clicked(mouse_input)
            mouse = {"position": mouse_position, "input": mouse_input, "click": mouse_click}

            self.clock.tick(60)
            self.clear_window()
            self.board()
            self.game_step()
            self.draw_shapes_in_game()
            self.text_box("Next", 10, 0, 4, 1, True)
            self.text_box(" ", 10, 1, 4, 13, False)
            self.draw_next_shapes()
            self.text_box("Score", 10, 14, 4, 1, True)
            self.text_box(str(self.score), 10, 15, 4, 2, False)
            self.text_box("Speed", 10, 17, 4, 1, True)
            self.text_box(str(int(self.speed)), 10, 18, 4, 2, False)

            self.last_click_status = mouse_input
            pg.display.update()

            if self.is_game_end(): # If the game has ended, show the restart button and wait for the player to click it to start a new game
                self.show_restart_button = True
                while True:
                    self.clear_window()
                    self.board()
                    self.draw_shapes_in_game()
                    self.text_box("Next", 10, 0, 4, 1, True)
                    self.text_box(" ", 10, 1, 4, 13, False)
                    self.draw_next_shapes()
                    self.text_box("Score", 10, 14, 4, 1, True)
                    self.text_box(str(self.score), 10, 15, 4, 2, False)
                    self.text_box("Speed", 10, 17, 4, 1, True)
                    self.text_box(str(int(self.speed)), 10, 18, 4, 2, False)
                    self.draw_restart_button()
                    
                    mouse_position = pg.mouse.get_pos()
                    mouse_input = pg.mouse.get_pressed()
                    mouse_click = self.mouse_has_clicked(mouse_input)
                    mouse = {"position": mouse_position, "input": mouse_input, "click": mouse_click}
                    self.restart_button_clicked(mouse)
                    
                    self.last_click_status = mouse_input
                    pg.display.update()
                    self.clock.tick(60)
                    
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            running = False
                            break
                    
                    if not self.show_restart_button:
                        break
                
                if not running:
                    break

        pg.quit()

if __name__ == "__main__":
    game = Tetris(42)
    game.run()
