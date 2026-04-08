import random
import numpy as np
import time
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("980x450")
        self.title("Battleships")

        #create arrays
        self.player_grid = np.full((10, 10), "", dtype=object)
        self.player_playing_grid = np.full((10, 10), "", dtype=object)
        self.preview_grid = np.full((10, 10), "", dtype=object)

        self.bot_grid = np.full((10, 10), "", dtype=object)
        self.bot_playing_grid = np.full((10, 10), "", dtype=object)
        self.heat_grid = np.full((10, 10), "", dtype=object)

        #initialize values
        self.ship_orientation = "horizontal"
        self.set_ship = False
        self.preview_cells = []
        self.player_sink_tally = 0
        self.bot_sink_tally = 0
        self.show_player_heatmap = False
        self.turns = 0
        self.placeable = None
        self.size = 10
        self.ships_placed = 0
        self.ships_hit = []
        self.auto_attack = False
        self.allow_auto_attack = False


        self.ships_index = [
            ("Mothership", 5),
            ("Battleship", 4),
            ("Submarines", 3),
            ("Cruiser", 3),
            ("Destroyer", 2)
        ]


        # layout of the UI
        self.controls = ctk.CTkFrame(self)
        self.controls.grid(row=1, column=0, padx=10, pady=10)

        self.player_board = ctk.CTkFrame(self)
        self.player_board.grid(row=1, column=1, padx=10, pady=10)

        self.bot_board = ctk.CTkFrame(self)
        self.bot_board.grid(row=1, column=2, padx=10, pady=10)

        self.board_label = ctk.CTkFrame(self,width=700, height=50)
        self.board_label.grid(row=0,rowspan=1,column=1, columnspan=2, padx=10, pady=10)

        #creating the boards
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

        self.turn_counter = ctk.CTkLabel(self.controls, text="Turns: 0", font=("Impact", 40))
        self.turn_counter.grid(row=6,column=0, padx=10, pady=10)

        self.auto_attack_btn = ctk.CTkButton(self.controls, text="Auto Place", command=self.toggle_auto_attack)
        self.auto_attack_btn.grid(row=4, column=0, pady=10)

    # function to create a 10x10 playing grid for the player
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

    # function to create a 10x10 playing grid for the bot
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
                    command=lambda r=i, c=j: self.null()
                )
                bot_buttons.grid(row=i, column=j, padx=1, pady=1)
                row_buttons.append(bot_buttons)
            self.bot_cells.append(row_buttons)
    def full_reset(self):
        self.player_grid = np.full((10, 10), "", dtype=object)
        self.player_playing_grid = np.full((10, 10), "", dtype=object)
        self.preview_grid = np.full((10, 10), "", dtype=object)
        self.bot_grid = np.full((10, 10), "", dtype=object)
        self.bot_playing_grid = np.full((10, 10), "", dtype=object)
        self.heat_grid = np.full((10, 10), "", dtype=object)
        self.ship_orientation = "horizontal"
        self.set_ship = False
        self.preview_cells = []
        self.player_sink_tally = 0
        self.bot_sink_tally = 0
        self.show_player_heatmap = False
        self.turns = 0
        self.placeable = None
        self.size = 10
        self.ships_placed = 0
        self.ships_hit = []
        self.reset_board_interface("player")
        self.reset_board_interface("bot")
        self.change_interface("Place your ship",": )")
        self.auto_attack = False
        self.allow_auto_attack = False
        self.auto_attack_btn.configure(text="Auto Place", fg_color="#1f6aa5")
        for i in range(10):
            for j in range(10):
                self.player_cells[i][j].configure(command=lambda r=i, c=j: self.cell_clicked(r, c))
        self.confirm_btn.configure(text="Confirm", command=self.confirm_place)
        self.versatile_btn.configure(text="Change to Vertical", command=self.rotate_ship_placement)
        self.turn_counter.configure(text="Turns: 0")

    #Quick interface changer for the face and the text
    def change_interface(self, text, face):
        if not text == "":
            self.terminal_text.configure(text=text)
        if not face == "":
            self.bot_face.configure(text=face)

    #Reset the board to full green again
    def reset_board_interface(self,board):
        for i in range(self.size):
            for j in range(self.size):
                if board == "player":
                   self.player_cells[i][j].configure(fg_color="#00FF00", text="",border_width=0,border_color="#00FF00")
                if board == "bot":
                    self.bot_cells[i][j].configure(fg_color="#00FF00", text="",border_width=0,border_color="#00FF00")

    # This function reconfigure each cell one by one to recolor the heat map
    def update_board(self):
        # --- HUNT MODE ---
        if bot_attack_method == "scan":
            for i in range(self.size):
                for j in range(self.size):
                    if self.bot_playing_grid[i][j] == "":
                        self.bot_cells[i][j].configure(
                            fg_color=value_to_green_red(self.heat_grid[i][j]),
                            text=self.heat_grid[i][j],
                            font=("Arial", 12, "normal")
                        )
            for x, y in get_biggest_cell(self.heat_grid):
                if self.bot_playing_grid[x][y] == "":
                    self.bot_cells[x][y].configure(text=f"{self.heat_grid[x][y]}!", font=("Arial", 16, "bold"))

        # --- SCAN MODE ---
        else:
            for i in range(self.size):
                for j in range(self.size):
                    if self.bot_playing_grid[i][j] == "":
                        self.bot_cells[i][j].configure(fg_color="#00FF00", text="", font=("Arial", 12, "normal"))

            # Mirror hunt logic to show on the board
            candidates = []
            for (hr, hc) in bot_last_hits:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = hr + dr, hc + dc
                    if (0 <= nr < 10 and 0 <= nc < 10
                            and self.bot_playing_grid[nr][nc] == ""
                            and (nr, nc) not in candidates):
                        candidates.append((nr, nc))

            if len(bot_last_hits) > 1:
                aligned = get_aligned(bot_last_hits, candidates)
                if aligned:
                    candidates = aligned

            for x, y in candidates:
                self.bot_cells[x][y].configure(fg_color="yellow", text="?", font=("Arial", 12, "bold"))


    # This function is behind every cell on the player's playing board
    def cell_clicked(self, row, col):
        self.clear_preview()
        print(f"Clicked {row+1}, {col+1}")
        if self.ships_placed >= len(self.ships_index):
            print("checked")
            return
        name, length = self.ships_index[self.ships_placed]
        if not self.can_place(row, col, length):
            self.change_interface("Out of Bounds","( ˶°ㅁ°) !!")
            return
        cells = []
        if self.ship_orientation == "horizontal":
            for i in range(length):
                cells.append((row, col + i))
        else:
            for i in range(length):
                cells.append((row + i, col))
        self.preview_cells = cells
        for r, c in cells:
            self.player_cells[r][c].configure(fg_color="yellow", text="?")
            self.change_interface("You Sure?", "( °ヮ° ) ?")
        if self.set_ship == True:
            self.player_grid[row, col] = 0
            self.update_board()

#This function checks if the player's ship position can be place
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

    #This function clears the preview from the previous temporary ship placement
    def clear_preview(self):
        for r, c in self.preview_cells:
            self.player_cells[r][c].configure(fg_color="#00FF00", text="",border_color="#00FF00")
        self.preview_cells = []

    #This function locks the ship placement in place.
    def confirm_place(self):
        #This part is when all ships are set and change all the cells and buttons commands to the attacking phase counterpart
        if self.ships_placed == len(self.ships_index):
            self.change_interface("LETS GOOO", "ᕙ(  •̀ ᗜ •́  )ᕗ")
            self.reset_board_interface("player")
            self.confirm_btn.configure(text="ATTACK!!!", command=lambda: self.confirm_attack())
            self.allow_auto_attack = True
            self.auto_attack_btn.configure(text="Auto: OFF")
            for i in range(self.size):
                for j in range(self.size):
                    self.player_cells[i][j].configure(command=lambda r=i, c=j: self.attack(r, c))
            self.bot_grid=place_ships_bot(self.bot_grid)
            self.allow_autoplay = True
            return
        #This part prevents skipping a ship if no placement is selected prior.
        if not self.preview_cells:
            return
        name, length = self.ships_index[self.ships_placed]
        row, col = self.preview_cells[0]
        #This part prevents skipping a ship the prior placement is invalid
        if not self.can_place(row, col, length):
            self.placeable = False
            return
        #Place the ship, mark it and increase the ship placed tally
        for r, c in self.preview_cells:
            self.player_grid[r][c] = name
            self.player_cells[r][c].configure(
                fg_color="red",
                text=name[0]
            )
            self.bot_cells[r][c].configure(border_color="blue", border_width=2)
        self.preview_cells = []
        self.ships_placed += 1
        self.change_interface("The Ship has sailed","ദ്ദി(ᵔᗜᵔ)")
        #Change the "Confirm" button to the "Play" button
        if self.ships_placed == len(self.ships_index):
            self.confirm_btn.configure(text="Play!!!")
            self.versatile_btn.configure(text="Reset", command = self.full_reset)


    #Change the ship placement orientation
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

    # ATTACK
    def attack(self,row,col):
        self.clear_preview()
        print(f"Clicked {row + 1}, {col + 1} attack")
        if self.can_attack(row,col):
            return
        if self.show_player_heatmap == True:
            return

    def can_attack(self,row,col):
        if self.player_playing_grid[row][col] == "":
            self.preview_cells.append((row,col))
            self.player_cells[row][col].configure(text = "?",border_color="red", border_width=2)
            return True
        else:
            return False

    def confirm_attack(self):
        #Prevents attacking nothing
        if not self.preview_cells:
            return
        #attack
        row, col = self.preview_cells[0]
        self.preview_cells = []
        self.player_playing_grid[row][col] = "x"
        result = self.check_attack("bot", row, col)
        if result in ("player win",):
            for i in range(10):
                for j in range(10):
                    self.player_cells[i][j].configure(command = self.null)
            return

        #The Bot attack immediately after the player finish attack
        x, y = bot_turn(self.bot_playing_grid, self.heat_grid)
        self.bot_playing_grid[x][y] = "x"
        self.check_attack("player", x, y)

        self.turns += 1
        self.turn_counter.configure(text=f"Turns: {str(self.turns)}")
        self.update_board()

        #Check the attack for both side if that's a miss, hit or sunk
    def check_attack(self, target, row, col):
        if target == "bot":
            ship_name = self.bot_grid[row][col]

            if ship_name == "":
                self.bot_grid[row][col] = "o"
                self.player_cells[row][col].configure(text="⚫", border_color="#00FF00")
                self.player_board_label.configure(text="Miss")
                return "miss"
            else:
                self.ships_hit.append((row, col))
                self.bot_grid[row][col] = "x"
                self.player_cells[row][col].configure(fg_color="red", text="🔴")

                if not np.any(self.bot_grid == ship_name):
                    self.player_board_label.configure(text = "You sunk a ship!!!")
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
            global bot_attack_method, bot_last_hits
            ship_name = self.player_grid[row][col]

            if ship_name == "":
                self.player_grid[row][col] = "o"
                self.bot_cells[row][col].configure(text="⚫", fg_color="#00FF00",font = ("Arial", 12, "normal"))
                self.bot_board_label.configure(text="Miss")
                return "miss"
            else:
                self.player_grid[row][col] = "x"
                self.bot_cells[row][col].configure(fg_color="red", text="🔴",font=("Arial", 12, "normal"))

                if not np.any(self.player_grid == ship_name):
                    self.change_interface(f"Bot sunk your ship!", "(ᗒᗣᗕ)՞")
                    self.bot_board_label.configure(text="Sink")
                    bot_attack_method = "scan"
                    bot_last_hits = []
                    self.bot_sink_tally += 1
                    if self.bot_sink_tally == 5:
                        self.change_interface("YOU LOSE", ": )))))")
                        self.auto_attack = False
                        self.auto_attack_btn.configure(text="Auto: OFF", fg_color="#1f6aa5")
                        return "bot win"
                    return "sink"
                else:
                    self.change_interface("Bot hit your ship!", "(ᗒᗣᗕ)՞")
                    self.bot_board_label.configure(text="Hit")
                    bot_attack_method = "hunt"
                    bot_last_hits.append((row, col))
                    return "hit"

        return None

    def toggle_auto_attack(self):
        if self.ships_placed < len(self.ships_index):
            self.auto_place_ships()
            return

        if self.allow_auto_attack == True:
            self.auto_attack = not self.auto_attack
            if self.auto_attack:
                self.auto_attack_btn.configure(text="Auto: ON", fg_color="green")
                self.run_auto_attack()
            else:
                self.auto_attack_btn.configure(text="Auto: OFF", fg_color="#1f6aa5")
    #Autoplace the REMAINING SHIPS
    def auto_place_ships(self):
        self.clear_preview()
        for i in range(self.size):
            for j in range(self.size):
                if self.player_grid[i][j] == "":
                    self.player_cells[i][j].configure(fg_color="#00FF00", text="")

        while self.ships_placed < len(self.ships_index):
            name, length = self.ships_index[self.ships_placed]
            placed = False
            while not placed:
                orientation = random.choice(["horizontal", "vertical"])
                self.ship_orientation = orientation
                if orientation == "horizontal":
                    row = random.randint(0, self.size - 1)
                    col = random.randint(0, self.size - length)
                else:
                    row = random.randint(0, self.size - length)
                    col = random.randint(0, self.size - 1)
                if self.can_place(row, col, length):
                    cells = [(row, col + i) for i in range(length)] if orientation == "horizontal" else [(row + i, col) for i in range(length)]
                    for r, c in cells:
                        self.player_grid[r][c] = name
                        self.player_cells[r][c].configure(fg_color="red", text=name[0])
                        self.bot_cells[r][c].configure(border_color="blue", border_width=2)
                    self.ships_placed += 1
                    placed = True

        self.confirm_btn.configure(text="Play!!!")
        self.versatile_btn.configure(text="Reset", command=self.full_reset)
        self.auto_attack_btn.configure(text="Auto: OFF", fg_color="#1f6aa5")
        self.change_interface("Ships placed!", "ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧")

    #Auto attack for the player (randomly)
    def run_auto_attack(self):
        if not self.auto_attack:
            return
        available = []
        for i in range(self.size):
            for j in range(self.size):
                if self.player_playing_grid[i][j] == "":
                    available.append((i, j))
        if not available:
            self.toggle_auto_attack()
            return

        self.clear_preview()
        row, col = random.choice(available)
        self.preview_cells.append((row, col))
        self.player_cells[row][col].configure(text="?", border_color="red", border_width=2)
        self.confirm_attack()

        # Wait 1s to play
        self.after(1000, self.run_auto_attack)

    #extra function to assign to a button when it needed to be a placebo one
    def null(self):
        return None

# ------BOT's AI--------
bot_attack_method = "scan"
bot_last_hits = []

#Randomly place ships, also avoid ship collision
def place_ships_bot(grid):
    ships = {
        "Mothership":    5,
        "Battleship": 4,
        "Submarines":    3,
        "Cruiser":    3,
        "Destroyer":  2,
    }

    for ship_name, size in ships.items():
        placed = False
        while not placed:
            direction = random.choice(["H", "V"])
            if direction == "H":
                row = random.randint(0, 9)
                col = random.randint(0, 10 - size)
                cells = [(row, col + i) for i in range(size)]
            else:
                row = random.randint(0, 10 - size)
                col = random.randint(0, 9)
                cells = [(row + i, col) for i in range(size)]

            if all(grid[r, c] == "" for r, c in cells):
                for r, c in cells:
                    grid[r, c] = ship_name[0]
                placed = True
    return grid

#This function determine the bot's next attack algorithm
def bot_turn(playing_grid, heat_grid):
    scan(playing_grid, heat_grid)  # always update heatmap first
    if bot_attack_method == "scan":
        return bot_attack(heat_grid)
    else:
        return hunt(playing_grid, heat_grid)

#This function send cells one by one to score the probability
def scan(current_grid,wanted_grid):
    for i in range(10):
        for j in range(10):
            wanted_grid[i, j] = (heat_map(current_grid, i, j))
    return wanted_grid

#This function check the neighbor of the
def hunt(playing_grid, heat_grid):
    global bot_last_hits, bot_attack_method
    candidates = []
    for (hr, hc) in bot_last_hits:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = hr + dr, hc + dc
            if (0 <= nr < 10 and 0 <= nc < 10
                    and playing_grid[nr][nc] == ""
                    and (nr, nc) not in candidates):
                candidates.append((nr, nc))
    if candidates:
        if len(bot_last_hits) > 1:
            aligned = get_aligned(bot_last_hits, candidates)
            if aligned:
                return random.choice(aligned)
        return random.choice(candidates)
    bot_attack_method = "scan"
    bot_last_hits = []
    return bot_attack(scan(playing_grid, heat_grid))

#align the next attack if the previous attack had figure out the opponent's ship's orientation
def get_aligned(hits, candidates):
    rows = [h[0] for h in hits]
    cols = [h[1] for h in hits]

    if len(set(rows)) == 1:
        return [(r, c) for r, c in candidates if r == rows[0]]
    elif len(set(cols)) == 1:
        return [(r, c) for r, c in candidates if c == cols[0]]
    return candidates

#Randomly attack the cells with the highest score
def bot_attack(heat_grid):
    possible_cells = get_biggest_cell(heat_grid)
    return random.choice(possible_cells)

#Search the heat grid to see what cell has the highest score and put them in a list
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

def heat_map(grid, x, y):
    #Avoid scoring cells that is not empty (hits,misses)
    if grid[x, y] != "":
        return 0
    rows, cols = 10, 10
    score = 0
    directions = [
        (-1, 0),
        ( 1, 0),
        ( 0,-1),
        ( 0, 1),]

    for dx, dy in directions:
        for step in range(1, 5):
            new_x = x + dx * step
            new_y = y + dy * step
            #check if this cell is out of bounds
            if not (0 <= new_x < rows and 0 <= new_y < cols):
                break
            #check if this cell is empty, immediately stop scoring that direction if it is blocked.
            if grid[new_x, new_y] == "":
                score += 1
            else:
                break
    return score

# A heat-map overlay, red means most likely to have a ship there.
def value_to_green_red(v):
    v = int(v)
    v = max(0, min(16, v))
    ratio = v / 16
    r = int(255 * ratio)
    g = int(255 * (1 - ratio))
    return f"#{r:02x}{g:02x}00"


# run
app = App()
app.mainloop()