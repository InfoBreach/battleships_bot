import random
import numpy as np
import time
from botools import place_ships_bot
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")



def value_to_green_red(v):
    v = int(v)
    v = max(0, min(16, v))
    ratio = v / 16
    r = int(255 * ratio)
    g = int(255 * (1 - ratio))
    return f"#{r:02x}{g:02x}00"




class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.placeable = None
        self.geometry("980x450")
        self.title("Battleships")

        self.size = 10

        #initialize values
        self.set_ship = False
        self.ship_orientation = "horizontal"

        # grids
        self.player_grid = np.full((10, 10), "", dtype=object) #keep player's ships positions
        self.player_playing_grid = np.full((10, 10), "", dtype=object) #keeps the position of the player's attack attempts.
        self.preview_grid = np.full((10, 10), "", dtype=object) #universal temporary grid, is cleared constantly

        self.bot_grid = np.full((10, 10), "", dtype=object) #keep bot's ships positions.
        self.bot_playing_grid = np.full((10, 10), "", dtype=object) #keep the position of the bot's attack attempts.
        self.heat_grid = np.full((10, 10), "", dtype=object) #keep track on how likely a ship is there

        self.preview_cells = []
        self.player_sink_tally = 0
        self.bot_sink_tally = 0
        self.show_player_heatmap = False

        self.ships_index = [
            ("Mothership", 5),
            ("Battleship", 4),
            ("Submarines", 3),
            ("Cruiser", 3),
            ("Destroyer", 2)
        ]
        self.ships_placed = 0
        self.ships_hit = []
        # layout
        self.controls = ctk.CTkFrame(self)
        self.controls.grid(row=1, column=0, padx=10, pady=10)

        self.player_board = ctk.CTkFrame(self)
        self.player_board.grid(row=1, column=1, padx=10, pady=10)

        self.bot_board = ctk.CTkFrame(self)
        self.bot_board.grid(row=1, column=2, padx=10, pady=10)

        self.board_label = ctk.CTkFrame(self,width=700, height=50)
        self.board_label.grid(row=0,rowspan=1,column=1, columnspan=2, padx=10, pady=10)

        # board
        self.player_cells = []
        self.bot_cells = []
        self.create_player_grid()
        self.create_bot_grid()

        self.player_board_label = ctk.CTkLabel(self.board_label,width=350, height=50,text="Player",font=("Arial", 20))
        self.player_board_label.grid(row=0, column=0, padx=10, pady=10)
        self.bot_board_label = ctk.CTkLabel(self.board_label,width=350, height=50,text="Bot",font=("Arial",20))
        self.bot_board_label.grid(row=0, column=9, padx=10, pady=10)

        # control button
        self.bot_face = ctk.CTkLabel(self.controls, text="(╥‸╥)", font=("Arial", 30))
        self.bot_face.grid(row=0, column=0, pady=10)

        self.versatile_btn = ctk.CTkButton(self.controls, text="Change to Vertical", command=self.rotate_ship_placement)
        self.versatile_btn.grid(row=3, column=0, pady=10)

        self.confirm_btn = ctk.CTkButton(self.controls, text="Confirm", command=self.confirm_place)
        self.confirm_btn.grid(row=2, column=0, pady=10)

        self.terminal_text = ctk.CTkLabel(self.controls,width=200, height=50, text="Set your ships", font=("Impact", 20))
        self.terminal_text.grid(row=1, column=0, pady=10)
    #  GRID
    def create_player_grid(self):
        for i in range(self.size):
            row_buttons = []
            for j in range(self.size):
                player_buttons = ctk.CTkButton(
                    self.player_board,
                    width=30,
                    height=30,
                    corner_radius=0,
                    text="",
                    fg_color="#00FF00",
                    text_color="black",
                    command=lambda r=i, c=j: self.cell_clicked(r, c)
                )
                player_buttons.grid(row=i, column=j, padx=1, pady=1)
                row_buttons.append(player_buttons)

            self.player_cells.append(row_buttons)

    def create_bot_grid(self):
        for i in range(self.size):
            row_buttons = []
            for j in range(self.size):
                bot_buttons = ctk.CTkButton(
                    self.bot_board,
                    width=30,
                    height=30,
                    corner_radius=0,
                    text="",
                    fg_color="#00FF00",
                    text_color="black",
                    command=lambda r=i, c=j: self.cell_clicked(r, c)
                )
                bot_buttons.grid(row=i, column=j, padx=1, pady=1)
                row_buttons.append(bot_buttons)

            self.bot_cells.append(row_buttons)

    def change_interface(self, text, face):
        if not text == "":
            self.terminal_text.configure(text=text)
        if not face == "":
            self.bot_face.configure(text=face)

    # LOGIC
    def cell_clicked(self, row, col):
        self.clear_preview()
        print(f"Clicked {row+1}, {col+1}")
        if self.ships_placed >= len(self.ships_index):
            print("checked")
            return

        name, length = self.ships_index[self.ships_placed]

        # check valid placement
        if not self.can_place(row, col, length):
            self.change_interface("Out of Bounds","( ˶°ㅁ°) !!")
            return

        # preview
        cells = []

        if self.ship_orientation == "horizontal":
            for i in range(length):
                cells.append((row, col + i))
        else:
            for i in range(length):
                cells.append((row + i, col))

        # store preview
        self.preview_cells = cells

        # draw preview (different color!)
        for r, c in cells:
            self.player_cells[r][c].configure(fg_color="yellow", text="?")
            self.change_interface("You Sure?", "( °ヮ° ) ?")

        if self.set_ship == True:
            self.player_grid[row, col] = 0


            self.update_board()

    def can_place(self, row, col, length):

        if self.ship_orientation == "horizontal":
            if col + length > self.size:
                self.placeable = False
                return False

            for i in range(length):
                if not self.player_grid[row][col + i] == "":
                    self.placeable = False
                    return False

        else:
            if row + length > self.size:
                self.placeable = False
                return False

            for i in range(length):
                if not self.player_grid[row + i][col] == "":
                    self.placeable = False
                    return False
        self.placeable = True
        return True

    def clear_preview(self):
        for r, c in self.preview_cells:
            self.player_cells[r][c].configure(fg_color="#00FF00", text="",border_color="#00FF00")
        self.preview_cells = []

    def update_board(self):
        for i in range(self.size):
            for j in range(self.size):
                self.bot_cells[i][j].configure(fg_color=value_to_green_red(self.player_grid[i][j]))

    def confirm_place(self):
        if self.ships_placed == len(self.ships_index):
            self.change_interface("LETS GOOO", "ᕙ(  •̀ ᗜ •́  )ᕗ")
            self.reset_board_interface("player")
            self.confirm_btn.configure(text="ATTACK!!!", command=lambda: self.confirm_attack())
            for i in range(self.size):
                for j in range(self.size):
                    self.player_cells[i][j].configure(command=lambda r=i, c=j: self.attack(r, c))
            self.bot_grid=place_ships_bot(self.bot_grid)
            for i in range(self.size):
                for j in range(self.size):
                    if not self.bot_grid[i][j] == "":
                        self.player_cells[i][j].configure(text="x")
            return

        # SAFETY: recompute validity instead of trusting old state
        if not self.preview_cells:
            return

        name, length = self.ships_index[self.ships_placed]
        row, col = self.preview_cells[0]

        if not self.can_place(row, col, length):
            self.placeable = False
            return

        # place ship
        for r, c in self.preview_cells:
            self.player_grid[r][c] = name
            self.player_cells[r][c].configure(
                fg_color="red",
                text=name[0]
            )
            self.bot_cells[r][c].configure(border_color="red", border_width=2)

        self.preview_cells = []
        self.ships_placed += 1

        self.change_interface("The Ship has sailed","ദ്ദി(ᵔᗜᵔ)")

        if self.ships_placed == len(self.ships_index):
            self.confirm_btn.configure(text="Play!!!")

    def rotate_ship_placement(self):
        if self.ship_orientation == "horizontal":
            self.ship_orientation = "vertical"
            self.terminal_text.configure(text="vertical")
            self.versatile_btn.configure(text="Change to Horizontal")
        elif self.ship_orientation == "vertical":
            self.ship_orientation = "horizontal"
            self.terminal_text.configure(text="horizontal")
            self.versatile_btn.configure(text="Change to Vertical")

        self.bot_face.pack_forget()

    def reset_board_interface(self,board):
        for i in range(self.size):
            for j in range(self.size):
                if board == "player":
                   self.player_cells[i][j].configure(fg_color="#00FF00", text="")
                if board == "bot":
                    self.bot_cells[i][j].configure(fg_color="#00FF00", text="")

    #ATTACK
    def attack(self,row,col):
        self.clear_preview()
        print(f"Clicked {row + 1}, {    col + 1} attack")
        if self.can_attack(row,col):
            return
        if self.show_player_heatmap == True:
            return
    # onebyone(self.player_grid, self.heat_grid, "heat_map")
    # self.player_cells[row][col].configure(text="0", fg_color="red")
    # time.sleep(0.5)

    def can_attack(self,row,col):
        if self.player_playing_grid[row][col] == "":
            self.preview_cells.append((row,col))
            self.player_cells[row][col].configure(text = "?",border_color="red", border_width=2)
            return True
        else:
            return False

    def confirm_attack(self):
        if not self.preview_cells:
            return

        row, col = self.preview_cells[0]
        self.preview_cells = []

        self.player_playing_grid[row][col] = "x"
        result = self.check_attack("bot", row, col)
        if result in ("player win",):
            return

        x, y = bot_turn(self.bot_playing_grid, self.heat_grid)
        self.bot_playing_grid[x][y] = "x"
        self.check_attack("player", x, y)

    def check_attack(self, target, row, col):
        if target == "bot":
            ship_name = self.bot_grid[row][col]  # grab first, before any branching

            if ship_name == "":
                self.bot_grid[row][col] = "o"
                self.player_cells[row][col].configure(text="⚫", border_color="#00FF00")
                self.change_interface("Miss!", "(╥‸╥)")
                return "miss"
            else:
                self.ships_hit.append((row, col))
                self.bot_grid[row][col] = "x"
                self.player_cells[row][col].configure(fg_color="red", text="🔴")

                if not np.any(self.bot_grid == ship_name):
                    self.change_interface("YOU sunk a ship", "ᕙ(  •̀ ᗜ •́  )ᕗ")
                    self.player_sink_tally += 1
                    if self.player_sink_tally == 5:
                        self.change_interface(f"YOU WIN", "ᕙ(  •̀ ᗜ •́  )ᕗ")
                        return "player win"
                    else:
                        return "sink"
                else:
                    self.change_interface("Hit!", "( °ヮ° )")
                    return "hit"

        elif target == "player":
            ship_name = self.player_grid[row][col]

            if ship_name == "":  # "0" is your empty cell value
                self.player_grid[row][col] = "o"
                self.bot_cells[row][col].configure(text="⚫", fg_color="#00FF00")
                return "miss"
            else:
                self.player_grid[row][col] = "x"
                self.bot_cells[row][col].configure(fg_color="red", text="🔴")

                if not np.any(self.player_grid == ship_name):
                    self.change_interface(f"Bot sunk your {ship_name}!", "(ᗒᗣᗕ)՞")
                    self.bot_sink_tally += 1
                    if self.bot_sink_tally == 5:
                        self.change_interface("YOU LOSE", "(ᗒᗣᗕ)՞")
                        return "bot win"
                    return "sink"
                else:
                    self.change_interface("Bot hit your ship!", "(ᗒᗣᗕ)՞")
                    return "hit"

        return None

def bot_turn(playing_grid, heat_grid):
    if True:
        return bot_attack(scan(playing_grid, heat_grid))
    else:
        return hunt(playing_grid, heat_grid)
def scan(current_grid,wanted_grid):
    for i in range(10):
        for j in range(10):
            wanted_grid[i, j] = (heat_map(current_grid, i, j))
    return wanted_grid

def bot_attack(heat_grid):
    possible_cells = get_biggest_cell(heat_grid)
    return random.choice(possible_cells)

def get_biggest_cell(grid):
    max_val = int(grid[0][0])
    positions = []

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            val = int(grid[i][j])

            if val > max_val:
                max_val = val
                positions = [(i, j)]

            elif val == max_val:
                positions.append((i, j))

    return positions

def heat_map(grid, row, col):
    if grid[row, col] != "":
        return 0
    rows, cols = 10, 10
    score = 0
    directions = [
        (-1, 0),  # Up
        ( 1, 0),  # Down
        ( 0,-1),  # Left
        ( 0, 1),]  # Right

    # Start scanning around
    for dr, dc in directions:
        for step in range(1, 5):
            new_row = row + dr * step
            new_col = col + dc * step

            if not (0 <= new_row < rows and 0 <= new_col < cols):
                break
            if grid[new_row, new_col] == "":
                score += 1
            else:
                break
    return score

# run
app = App()
app.mainloop()