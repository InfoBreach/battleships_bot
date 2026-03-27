import numpy as np
import time
from botools import onebyone
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

        self.geometry("570x350")
        self.title("Battleships")

        self.size = 10

        #initialize values
        self.set_ship = False
        self.ship_orientation = "horizontal"

        # grids
        self.player_grid = np.full((10, 10), "0", dtype=object)
        self.heat_grid = np.full((10, 10), "-", dtype=object)
        self.preview_grid = np.full((10, 10), "-", dtype=object)

        self.preview_cells = []

        self.ships_index = [
            ("Mothership", 5),
            ("Battleship", 4),
            ("Submarines", 3),
            ("Cruiser", 3),
            ("Destroyer", 2)
        ]
        self.ships_placed = 0
        # layout
        self.controls = ctk.CTkFrame(self)
        self.controls.grid(row=0, column=0, padx=10, pady=10)

        self.sea = ctk.CTkFrame(self)
        self.sea.grid(row=0, column=1, padx=10, pady=10)

        # board
        self.buttons = []
        self.create_grid()

        # control button
        self.bot_face = ctk.CTkLabel(self.controls, text="(╥‸╥)", font=("Arial", 30))
        self.bot_face.grid(row=0, column=0, pady=10)

        self.versatile_btn = ctk.CTkButton(self.controls, text="Change to Vertical", command=self.rotate_ship_placement)
        self.versatile_btn.grid(row=3, column=0, pady=10)

        self.confirm_btn = ctk.CTkButton(self.controls, text="Confirm", command=self.confirm)
        self.confirm_btn.grid(row=2, column=0, pady=10)

        self.terminal_text = ctk.CTkLabel(self.controls,width=200, height=50, text="Set your ships", font=("Impact", 20))
        self.terminal_text.grid(row=1, column=0, pady=10)
    #  GRID
    def create_grid(self):
        for i in range(self.size):
            row_buttons = []
            for j in range(self.size):
                btn = ctk.CTkButton(
                    self.sea,
                    width=30,
                    height=30,
                    corner_radius=0,
                    text=self.player_grid[i][j],
                    fg_color=value_to_green_red(self.player_grid[i][j]),
                    text_color="black",
                    command=lambda r=i, c=j: self.cell_clicked(r, c)
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                row_buttons.append(btn)

            self.buttons.append(row_buttons)

    # LOGIC
    def cell_clicked(self, row, col):
        self.clear_preview()
        print(f"Clicked {row+1}, {col+1}")
        if self.ships_placed >= len(self.ships_index):
            return

        name, length = self.ships_index[self.ships_placed]

        # check valid placement
        if not self.can_place(row, col, length):
            self.terminal_text.configure(text="Out of Bounds")
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
            self.buttons[r][c].configure(fg_color="yellow", text="P")
            self.terminal_text.configure(text="You Sure?")
            self.bot_face.configure(text="( °ヮ° ) ?")


        if self.set_ship == True:
            self.player_grid[row, col] = 0

            onebyone(self.player_grid, self.heat_grid, "heat_map")
            self.buttons[row][col].configure(text="0", fg_color="red")
            time.sleep(0.5)

            self.update_board()

    def can_place(self, row, col, length):

        if self.ship_orientation == "horizontal":
            if col + length > self.size:
                return False

            for i in range(length):
                if not self.player_grid[row][col + i] == "0":
                    return False

        else:
            if row + length > self.size:
                return False

            for i in range(length):
                if self.player_grid[row + i][col] == "S":
                    return False

        return True
    def clear_preview(self):

        for r, c in self.preview_cells:
            # restore from actual grid
            value = self.player_grid[r][c]

            if value == "S":
                color = "red"
            else:
                color = "#00FF00"

            self.buttons[r][c].configure(fg_color=color, text=value)

        self.preview_cells = []

    def update_board(self):
        for i in range(self.size):
            for j in range(self.size):
                self.buttons[i][j].configure(
                    text=self.player_grid[i][j],
                    fg_color=value_to_green_red(self.player_grid[i][j])
                )

    def confirm(self):

        if not self.preview_cells:
            self.terminal_text.configure(text="LETS GOOO")
            self.bot_face.configure(text="ᕙ(  •̀ ᗜ •́  )ᕗ")
            return

        for r, c in self.preview_cells:
            self.player_grid[r][c] = self.ships_index[self.ships_placed][0]
            self.buttons[r][c].configure(fg_color="red", text=self.ships_index[self.ships_placed][0][0])

        self.preview_cells = []
        self.ships_placed += 1
        self.terminal_text.configure(text="The Ship have sailed")
        self.bot_face.configure(text=" ദ്ദി(ᵔᗜᵔ)")
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


# run
app = App()
app.mainloop()