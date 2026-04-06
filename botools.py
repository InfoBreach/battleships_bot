
import random

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
            if all(grid[r, c] == "" for r, c in cells):
                for r, c in cells:
                    grid[r, c] = ship_name[0]
                placed = True
    return grid

