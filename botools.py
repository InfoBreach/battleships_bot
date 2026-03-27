import numpy as np
import random


def onebyone(current_grid,wanted_grid,function):
    if function == "heat_map":
        for i in range(10):
            for j in range(10):
                wanted_grid[i, j] = (heat_map(current_grid, i, j))
        return wanted_grid
    else:
        return None


def attack(heat_grid):
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
    if grid[row, col] != "-":
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
            if grid[new_row, new_col] == "-":
                score += 1
            else:
                break
    return score

def place_ships_bot(grid):
    """Randomly place all battleship ships on the grid without collisions."""
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
            direction = random.choice(["H", "V"])  # Horizontal or Vertical
            if direction == "H":
                row = random.randint(0, 9)
                col = random.randint(0, 10 - size)  # Ensure it fits
                cells = [(row, col + i) for i in range(size)]
            else:
                row = random.randint(0, 10 - size)  # Ensure it fits
                col = random.randint(0, 9)
                cells = [(row + i, col) for i in range(size)]

            # Check no collision with existing ships
            if all(grid[r, c] == "-" for r, c in cells):
                for r, c in cells:
                    grid[r, c] = ship_name[0]
                placed = True

    return grid