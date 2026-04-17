from dataclasses import dataclass, field
import random
import numpy as np
import customtkinter as ctk
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SIZE = 10
SHIPS_INDEX = [
    ("Mothership", 5),
    ("Battleship", 4),
    ("Submarines", 3),
    ("Cruiser", 3),
    ("Destroyer", 2),
]

# --- Ship ---
@dataclass
class Ship:
    #Clasify a ship
    name: str
    length: int
    cells: list[tuple[int, int]] = field(default_factory=list)

    def is_sunk(self, grid: np.ndarray) -> bool:
        #This will turn true when all cells of this ship are hit
        return all(grid[r][c] == "x" for r, c in self.cells)

    @property
    def initial(self) -> str:
        return self.name[0]

# --- Board ---
class Board:
    def __init__(self):
        self.grid = np.full((SIZE, SIZE), "", dtype=object)
        self.playing_grid = np.full((SIZE, SIZE), "", dtype=object)
        self.ships: list[Ship] = []

    # --- Placement ---

    def can_place(self, row: int, col: int, length: int, orientation: str) -> bool:
        if orientation == "horizontal":
            if col + length > SIZE:
                return False
            return all(self.grid[row][col + i] == "" for i in range(length))
        else:
            if row + length > SIZE:
                return False
            return all(self.grid[row + i][col] == "" for i in range(length))

    def place_ship(self, ship: Ship, row: int, col: int, orientation: str):
        cells = (
            [(row, col + i) for i in range(ship.length)]
            if orientation == "horizontal"
            else [(row + i, col) for i in range(ship.length)]
        )
        ship.cells = cells
        for r, c in cells:
            self.grid[r][c] = ship.name
        self.ships.append(ship)

    def place_ship_random(self, ship: Ship):
        #Place a ship at a random valid position.
        placed = False
        while not placed:
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                row = random.randint(0, SIZE - 1)
                col = random.randint(0, SIZE - ship.length)
            else:
                row = random.randint(0, SIZE - ship.length)
                col = random.randint(0, SIZE - 1)
            if self.can_place(row, col, ship.length, orientation):
                self.place_ship(ship, row, col, orientation)
                placed = True

    # Attack checker
    def receive_attack(self, row: int, col: int) -> tuple[str, Ship | None]:
        self.playing_grid[row][col] = "x"
        ship_name = self.grid[row][col]

        if ship_name == "":
            self.grid[row][col] = "o"
            return "miss", None

        self.grid[row][col] = "x"
        ship = self._find_ship(ship_name)
        if ship and ship.is_sunk(self.grid):
            return "sink", ship
        return "hit", ship

    def _find_ship(self, name: str) -> Ship | None:
        return next((s for s in self.ships if s.name == name), None)

    def all_sunk(self) -> bool:
        return all(ship.is_sunk(self.grid) for ship in self.ships)

    def reset(self):
        self.grid = np.full((SIZE, SIZE), "", dtype=object)
        self.playing_grid = np.full((SIZE, SIZE), "", dtype=object)
        self.ships = []

# --- Bot's algorithm ---
class BotAI:
    def __init__(self):
        self.attack_method = "scan"
        self.last_hits: list[tuple[int, int]] = []
        self.remaining_ships: list[int] = [5, 4, 3, 3, 2]
        self.heat_grid = np.zeros((SIZE, SIZE), dtype=int)

    # --- Command center ---

    def next_attack(self, playing_grid: np.ndarray) -> tuple[int, int]:
        #Return the cell (row, col) the bot will attack next.
        self._update_heat(playing_grid)
        if self.attack_method == "scan":
            return self._scan_attack()
        return self._hunt_attack(playing_grid)

    def on_hit(self, row: int, col: int):
        #Notify the bot that it hit a ship
        self.attack_method = "hunt"
        self.last_hits.append((row, col))

    def on_sink(self, ship: Ship):
        #Notify the bot that a ship had sink
        sunk_cells = set(ship.cells)
        self.last_hits = [(r, c) for (r, c) in self.last_hits if (r, c) not in sunk_cells]
        self.attack_method = "hunt" if self.last_hits else "scan"
        if ship.length in self.remaining_ships:
            self.remaining_ships.remove(ship.length)

    @property
    def max_heat_score(self) -> int:
        #Maximum theoretical heatmap score given the current remaining ships, use for the overlays.
        return max(sum(length * 2 for length in self.remaining_ships), 1) if self.remaining_ships else 1

    def reset(self):
        self.attack_method = "scan"
        self.last_hits = []
        self.remaining_ships = [5, 4, 3, 3, 2]
        self.heat_grid = np.zeros((SIZE, SIZE), dtype=int)

    # --- Bot's thinking system ---

    def _update_heat(self, playing_grid: np.ndarray):
        #The heatmap overlay
        for i in range(SIZE):
            for j in range(SIZE):
                self.heat_grid[i][j] = self._heat_at(playing_grid, i, j)

    def _heat_at(self, grid: np.ndarray, x: int, y: int) -> int:
        #Score each cells base on the chance that it have a ship there
        if grid[x, y] != "":
            return -1
        score = 0
        for length in self.remaining_ships:
            for start in range(length):
                c0 = y - start
                if 0 <= c0 and c0 + length <= SIZE:
                    if all(grid[x, c0 + k] == "" for k in range(length)):
                        score += 1
                r0 = x - start
                if 0 <= r0 and r0 + length <= SIZE:
                    if all(grid[r0 + k, y] == "" for k in range(length)):
                        score += 1
        return score

    def _scan_attack(self) -> tuple[int, int]:
        return random.choice(self._best_cells())

    def _hunt_attack(self, playing_grid: np.ndarray) -> tuple[int, int]:
        candidates = []
        # This method is to prevent the bot ignore adjacent ships problem (like the last version)
        # Look for adjacent hit pairs to establish a line (horizontal or vertical)
        for r1, c1 in self.last_hits:
            for r2, c2 in self.last_hits:
                # Horizontal adjacency
                if r1 == r2 and abs(c1 - c2) == 1:
                    left_col = min(c1, c2) - 1
                    right_col = max(c1, c2) + 1
                    if left_col >= 0 and playing_grid[r1][left_col] == "":
                        candidates.append((r1, left_col))
                    if right_col < SIZE and playing_grid[r1][right_col] == "":
                        candidates.append((r1, right_col))

                # Vertical adjacency
                elif c1 == c2 and abs(r1 - r2) == 1:
                    up_row = min(r1, r2) - 1
                    down_row = max(r1, r2) + 1
                    if up_row >= 0 and playing_grid[up_row][c1] == "":
                        candidates.append((up_row, c1))
                    if down_row < SIZE and playing_grid[down_row][c1] == "":
                        candidates.append((down_row, c1))

        # Remove duplicates
        candidates = list(set(candidates))
        if candidates:
            return random.choice(candidates)

        # If no lines found (first hit, or stray hits from when trying to hunt another ship)
        # Then focus only on the neighbors of the most recent hit to prevent getting distracted.
        for hr, hc in reversed(self.last_hits):
            local_candidates = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = hr + dr, hc + dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE and playing_grid[nr][nc] == "":
                    local_candidates.append((nr, nc))
            if local_candidates:
                return random.choice(local_candidates)

        #Failsafe, if all known hits are SOMEHOW fully surrounded by misses/hits :0
        self.attack_method = "scan"
        self.last_hits = []
        return self._scan_attack()

    def _aligned_candidates(self, candidates: list[tuple[int, int]]) -> list[tuple[int, int]]:
        # this function is retired, BUT it is still useful to show as an overlay
        rows = [h[0] for h in self.last_hits]
        cols = [h[1] for h in self.last_hits]
        if len(set(rows)) == 1:
            return [(r, c) for r, c in candidates if r == rows[0]]
        if len(set(cols)) == 1:
            return [(r, c) for r, c in candidates if c == cols[0]]
        return candidates

    def _best_cells(self) -> list[tuple[int, int]]:
        #Randomly pick amongst the highest value cells
        max_val = -1
        positions = []
        for i in range(SIZE):
            for j in range(SIZE):
                val = int(self.heat_grid[i][j])
                if val > max_val:
                    max_val = val
                    positions = [(i, j)]
                elif val == max_val:
                    positions.append((i, j))
        return positions


#--- Other ---
def heat_color(value: int, max_score: int) -> str:
    #
    v = max(0, min(max_score, value))
    ratio = v / max_score
    r = int(255 * ratio)
    g = int(255 * (1 - ratio))
    return f"#{r:02x}{g:02x}00"

# --- App UI ----
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.auto_attack_delay = 500
        self.auto_repeat = True

        self.geometry("980x450")
        self.title("Battleships")

        # Domain objects
        self.player_board = Board()
        self.bot_board = Board()
        self.bot_ai = BotAI()

        # UI state
        self.ship_orientation = "horizontal"
        self.preview_cells: list[tuple[int, int]] = []
        self.ships_placed = 0
        self.auto_attack = False
        self.allow_auto_attack = False
        self.player_sink_tally = 0
        self.bot_sink_tally = 0
        self.turns = 0

        self._build_ui()
        self.font_normal = ctk.CTkFont("Arial", 12, "normal")
        self.font_bold = ctk.CTkFont("Arial", 16, "bold")
        self.font_hunt = ctk.CTkFont("Arial", 12, "bold")
    # Creates UIs

    def _build_ui(self):
        self.controls = ctk.CTkFrame(self)
        self.controls.grid(row=1, column=0, padx=10, pady=10)

        self.player_board_frame = ctk.CTkFrame(self)
        self.player_board_frame.grid(row=1, column=1, padx=10, pady=10)

        self.bot_board_frame = ctk.CTkFrame(self)
        self.bot_board_frame.grid(row=1, column=2, padx=10, pady=10)

        self.board_label = ctk.CTkFrame(self, width=700, height=50)
        self.board_label.grid(row=0, rowspan=1, column=1, columnspan=2, padx=10, pady=10)

        self.player_cells: list[list[ctk.CTkButton]] = []
        self.bot_cells: list[list[ctk.CTkButton]] = []
        self._create_player_grid()
        self._create_bot_grid()

        self.player_board_label = ctk.CTkLabel(self.board_label, width=350, height=50, text="Player", font=("Arial", 20))
        self.player_board_label.grid(row=0, column=0, padx=10, pady=10)
        self.bot_board_label = ctk.CTkLabel(self.board_label, width=350, height=50, text="Bot", font=("Arial", 20))
        self.bot_board_label.grid(row=0, column=9, padx=10, pady=10)

        self.bot_face = ctk.CTkLabel(self.controls, text="﹏𓊝﹏", font=("Arial", 30))
        self.bot_face.grid(row=0, column=0, pady=10)

        self.terminal_text = ctk.CTkLabel(self.controls, width=200, height=50, text="Set your ships", font=("Impact", 20))
        self.terminal_text.grid(row=1, column=0, pady=10)

        self.confirm_btn = ctk.CTkButton(self.controls, text="Confirm", command=self.confirm_place)
        self.confirm_btn.grid(row=2, column=0, pady=10)

        self.versatile_btn = ctk.CTkButton(self.controls, text="Change to Vertical", command=self.rotate_orientation)
        self.versatile_btn.grid(row=3, column=0, pady=10)

        self.auto_attack_btn = ctk.CTkButton(self.controls, text="Auto Place", command=self.toggle_auto_attack)
        self.auto_attack_btn.grid(row=4, column=0, pady=10)

        self.turn_counter = ctk.CTkLabel(self.controls, text="Turns: 0", font=("Impact", 40))
        self.turn_counter.grid(row=6, column=0, padx=10, pady=10)

    def _create_player_grid(self):
        for i in range(SIZE):
            row_buttons = []
            for j in range(SIZE):
                btn = ctk.CTkButton(
                    self.player_board_frame, width=30, height=30, corner_radius=0,
                    text="", fg_color="#00FF00", text_color="black",
                    command=lambda r=i, c=j: self.cell_clicked(r, c)
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                row_buttons.append(btn)
            self.player_cells.append(row_buttons)

    def _create_bot_grid(self):
        for i in range(SIZE):
            row_buttons = []
            for j in range(SIZE):
                btn = ctk.CTkButton(
                    self.bot_board_frame, width=30, height=30, corner_radius=0,
                    text="", fg_color="#00FF00", text_color="black",
                    command=self.null
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                row_buttons.append(btn)
            self.bot_cells.append(row_buttons)

    # UIs changer

    def set_status(self, text: str = "", face: str = ""):
        if text:
            self.terminal_text.configure(text=text)
        if face:
            self.bot_face.configure(text=face)

    def reset_board_colors(self, board: str):
        cells = self.player_cells if board == "player" else self.bot_cells
        for i in range(SIZE):
            for j in range(SIZE):
                cells[i][j].configure(fg_color="#00FF00", text="", border_width=0, border_color="#00FF00")

    def update_heatmap_display(self):
        # Redraw the overlay after every move
        playing = self.player_board.playing_grid

        # If game over, dont update
        if not self.bot_ai.remaining_ships or self.player_sink_tally == 5:
            for i in range(SIZE):
                for j in range(SIZE):
                    if playing[i][j] == "":
                        self.bot_cells[i][j].configure(fg_color="#00FF00", text="")
            return

        # Heatmap overlay
        if self.bot_ai.attack_method == "scan":
            max_score = self.bot_ai.max_heat_score
            best_cells = set(self.bot_ai._best_cells())

            for i in range(SIZE):
                for j in range(SIZE):
                    if playing[i][j] == "":
                        score = int(self.bot_ai.heat_grid[i][j])
                        text = f"{score}!" if (i, j) in best_cells else str(score)

                        # Use the pre-cached fonts here
                        current_font = self.font_bold if (i, j) in best_cells else self.font_normal

                        self.bot_cells[i][j].configure(
                            fg_color=heat_color(score, max_score),
                            text=text,
                            font=current_font
                        )

        # Adjacent overlay
        else:
            for i in range(SIZE):
                for j in range(SIZE):
                    if playing[i][j] == "":
                        self.bot_cells[i][j].configure(fg_color="#00FF00", text="", font=self.font_normal)

            candidates = []
            for hr, hc in self.bot_ai.last_hits:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = hr + dr, hc + dc
                    if (0 <= nr < SIZE and 0 <= nc < SIZE
                            and playing[nr][nc] == ""
                            and (nr, nc) not in candidates):
                        candidates.append((nr, nc))

            if len(self.bot_ai.last_hits) > 1:
                aligned = self.bot_ai._aligned_candidates(candidates)
                if aligned:
                    candidates = aligned

            for x, y in candidates:
                self.bot_cells[x][y].configure(fg_color="yellow", text="?", font=self.font_hunt)

    # Ship placement phase

    def cell_clicked(self, row: int, col: int):
        self._clear_preview()
        if self.ships_placed >= len(SHIPS_INDEX):
            return
        name, length = SHIPS_INDEX[self.ships_placed]
        if not self.player_board.can_place(row, col, length, self.ship_orientation):
            self.set_status("Out of Bounds", "( ˶°ㅁ°) !!")
            return
        cells = (
            [(row, col + i) for i in range(length)]
            if self.ship_orientation == "horizontal"
            else [(row + i, col) for i in range(length)]
        )
        self.preview_cells = cells
        for r, c in cells:
            self.player_cells[r][c].configure(fg_color="yellow", text="?")
        self.set_status("You Sure?", "( °ヮ° ) ?")

    def confirm_place(self):
        if self.ships_placed == len(SHIPS_INDEX):
            self._start_combat_phase()
            return
        if not self.preview_cells:
            return
        name, length = SHIPS_INDEX[self.ships_placed]
        row, col = self.preview_cells[0]
        if not self.player_board.can_place(row, col, length, self.ship_orientation):
            return
        ship = Ship(name, length)
        self.player_board.place_ship(ship, row, col, self.ship_orientation)
        for r, c in self.preview_cells:
            self.player_cells[r][c].configure(fg_color="red", text=ship.initial)
            self.bot_cells[r][c].configure(border_color="blue", border_width=2)
        self.preview_cells = []
        self.ships_placed += 1
        self.set_status("Noted. I'll sink it.", "( ͡~ ͜ʖ ͡°)")
        if self.ships_placed == len(SHIPS_INDEX):
            self.confirm_btn.configure(text="Play!!!")
            self.set_status("Finally. Let's go.", "(ง'̀-'́)ง")
            self.versatile_btn.configure(text="Reset", command=self.full_reset)

    def _start_combat_phase(self):
        self.set_status("Alright, take your shot.", "( ͡° ͜ʖ ͡°)")
        self.reset_board_colors("player")
        self.confirm_btn.configure(text="ATTACK!!!", command=self.confirm_attack)
        self.allow_auto_attack = True
        self.auto_attack_btn.configure(text="Auto: OFF")
        for i in range(SIZE):
            for j in range(SIZE):
                self.player_cells[i][j].configure(command=lambda r=i, c=j: self.stage_attack(r, c))
        for name, length in SHIPS_INDEX:
            self.bot_board.place_ship_random(Ship(name, length))

    def rotate_orientation(self):
        if self.ship_orientation == "horizontal":
            self.ship_orientation = "vertical"
            self.terminal_text.configure(text="vertical")
            self.versatile_btn.configure(text="Change to Horizontal")
        else:
            self.ship_orientation = "horizontal"
            self.terminal_text.configure(text="horizontal")
            self.versatile_btn.configure(text="Change to Vertical")

    def auto_place_ships(self):
        self._clear_preview()
        for i in range(SIZE):
            for j in range(SIZE):
                if self.player_board.grid[i][j] == "":
                    self.player_cells[i][j].configure(fg_color="#00FF00", text="")
        while self.ships_placed < len(SHIPS_INDEX):
            name, length = SHIPS_INDEX[self.ships_placed]
            ship = Ship(name, length)
            self.player_board.place_ship_random(ship)
            for r, c in ship.cells:
                self.player_cells[r][c].configure(fg_color="red", text=ship.initial)
                self.bot_cells[r][c].configure(border_color="blue", border_width=2)
            self.ships_placed += 1
        self.confirm_btn.configure(text="Play!!!")
        self.versatile_btn.configure(text="Reset", command=self.full_reset)
        self.auto_attack_btn.configure(text="Auto: OFF", fg_color="#1f6aa5")
        self.set_status("Lazy, do better", "(¬､¬)")

    def _clear_preview(self):
        for r, c in self.preview_cells:
            self.player_cells[r][c].configure(fg_color="#00FF00", text="", border_color="#00FF00")
        self.preview_cells = []

    # --- Combat phase ---

    def stage_attack(self, row: int, col: int):
        #Gives a preview of your next attack
        self._clear_preview()
        if self.bot_board.playing_grid[row][col] == "":
            self.preview_cells.append((row, col))
            self.player_cells[row][col].configure(text="?", border_color="red", border_width=2)

    def confirm_attack(self):
        if not self.preview_cells:
            return
        row, col = self.preview_cells.pop()
        self.preview_cells = []

        # Player attacks bot
        result = self._resolve_player_attack(row, col)
        if result == "player win":
            for i in range(SIZE):
                for j in range(SIZE):
                    self.player_cells[i][j].configure(command=self.null)
            return

        # Bot automatically attacks player
        bx, by = self.bot_ai.next_attack(self.player_board.playing_grid)
        self._resolve_bot_attack(bx, by)

        self.turns += 1
        self.turn_counter.configure(text=f"Turns: {self.turns}")
        self.update_heatmap_display()

    def _resolve_player_attack(self, row: int, col: int) -> str | None:
        #Check if the player's attack miss, hit or sink a bot's ship
        result, ship = self.bot_board.receive_attack(row, col)

        if result == "miss":
            self.player_cells[row][col].configure(text="⚫", border_color="#00FF00")
            self.player_board_label.configure(text="Miss")
            self.set_status(
                random.choice(["Haha, missed!", "Is that your best?"]),
                random.choice(["( ͡~ ͜ʖ ͡°)", "¯\\_(ツ)_/¯", "lol"])
            )
        elif result == "hit":
            self.player_cells[row][col].configure(fg_color="red", text="🔴")
            self.set_status(
                random.choice(["Lucky shot...", "That hurt a bit", "ok fine"]),
                random.choice(["(-.-)", "(¬_¬)", ">:("])
            )
        elif result == "sink":
            self.player_cells[row][col].configure(fg_color="red", text="🔴")
            self.player_board_label.configure(text="You sunk a ship!!!")
            self.set_status(
                random.choice(["Ok you got one", "Sus", "Fluke."]),
                random.choice(["(¬､¬)", "(._.)", "ඞ"])
            )
            self.player_sink_tally += 1
            if self.player_sink_tally == 5:
                self.set_status("Fine. You win.", "( ╥﹏╥ )")
                return "player win"

        return result

    def _resolve_bot_attack(self, row: int, col: int) -> str | None:
        #same as above but with update overlays and change algorithm when needed.
        result, ship = self.player_board.receive_attack(row, col)

        if result == "miss":
            self.bot_cells[row][col].configure(text="⚫", fg_color="#00FF00", font=("Arial", 12, "normal"))
            self.bot_board_label.configure(text="Miss")
            self.set_status(
                random.choice(["Ugh, I'll get you", "Just warming up", "Next one's yours"]),
                random.choice(["(¬_¬)", "(-.-)", "˙◠˙"])
            )
        elif result == "hit":
            self.bot_cells[row][col].configure(fg_color="red", text="🔴", font=("Arial", 12, "normal"))
            self.bot_board_label.configure(text="Hit")
            self.bot_ai.on_hit(row, col)
            self.set_status(
                random.choice(["HA! Direct hit!", "Gotcha!", "Too easy"]),
                random.choice(["( ≧▽≦)", "(ง •̀_•́)ง", ":V"])
            )
        elif result == "sink":
            self.bot_cells[row][col].configure(fg_color="red", text="🔴", font=("Arial", 12, "normal"))
            self.bot_board_label.configure(text="Sink")
            self.bot_ai.on_sink(ship)
            self.set_status(
                random.choice(["YOOO I SUNK IT", "Bye bye ship", "Another one down!!"]),
                random.choice(["ᕙ(▀̿̿ĺ̯▀̿ ̿)ᕗ", "(ง'̀-'́)ง", "GET REKT"])
            )
            self.bot_sink_tally += 1
            if self.bot_sink_tally == 5:
                self.set_status("YOU LOSE", ": )))))")
                self.auto_attack = False
                self.auto_attack_btn.configure(text="Auto: OFF", fg_color="#1f6aa5")
                for i in range(SIZE):
                    for j in range(SIZE):
                        if self.player_board.playing_grid[i][j] == "":
                            self.bot_cells[i][j].configure(text="")
                self.update_heatmap_display()
                if self.auto_repeat:
                    self.after(2000, self._auto_repeat_restart)
                return "bot win"

    # --- Auto-attack ---

    def toggle_auto_attack(self):
        if self.ships_placed < len(SHIPS_INDEX):
            self.auto_place_ships()
            return
        if self.allow_auto_attack:
            self.auto_attack = not self.auto_attack
            if self.auto_attack:
                self.auto_attack_btn.configure(text="Auto: ON", fg_color="green")
                self.run_auto_attack()
            else:
                self.auto_attack_btn.configure(text="Auto: OFF", fg_color="#1f6aa5")

    def run_auto_attack(self):
        if not self.auto_attack:
            return
        available = [(i, j) for i in range(SIZE) for j in range(SIZE)if self.bot_board.playing_grid[i][j] == ""]
        if not available:
            self.toggle_auto_attack()
            return
        self._clear_preview()
        row, col = random.choice(available)
        self.preview_cells.append((row, col))
        self.player_cells[row][col].configure(text="?", border_color="red", border_width=2)
        self.confirm_attack()
        self.after(self.auto_attack_delay, self.run_auto_attack)

    def _auto_repeat_restart(self):
        self.full_reset()
        self.auto_place_ships()
        self.confirm_place()
        time.sleep(1)
        self.auto_attack = True
        self.auto_attack_btn.configure(text="Auto: ON", fg_color="green")
        self.run_auto_attack()

    # --- Reset ---

    def full_reset(self):
        self.player_board.reset()
        self.bot_board.reset()
        self.bot_ai.reset()

        self.ship_orientation = "horizontal"
        self.preview_cells = []
        self.ships_placed = 0
        self.player_sink_tally = 0
        self.bot_sink_tally = 0
        self.turns = 0

        self.reset_board_colors("player")
        self.reset_board_colors("bot")

        if not self.auto_repeat:
            self.auto_attack = False
            self.allow_auto_attack = False

        self.set_status("Place your ship", ": )")
        self.auto_attack_btn.configure(text="Auto Place", fg_color="#1f6aa5")
        self.confirm_btn.configure(text="Confirm", command=self.confirm_place)
        self.versatile_btn.configure(text="Change to Vertical", command=self.rotate_orientation)
        self.turn_counter.configure(text="Turns: 0")
        for i in range(SIZE):
            for j in range(SIZE):
                self.player_cells[i][j].configure(command=lambda r=i, c=j: self.cell_clicked(r, c))

    # a function to do nothing, assign to a button to turn it into a placebo one.
    def null(self):
        return None


# just run :)
app = App()
app.mainloop()