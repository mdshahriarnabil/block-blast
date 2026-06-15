"\"\"\"Definitions for every block-shape the player can place.

Each piece is a list of (row, col) offsets relative to its top-left
corner. Keeping shapes as plain data (not classes) makes it easy for
beginners to read and extend with new pieces.
\"\"\"

import random
from .constants import NEON_COLORS

# A library of shapes inspired by the classic Block Blast / tetromino set.
# Feel free to add more!  Just list the filled cells as (row, col).
SHAPES = [
    # --- single + tiny ---
    [(0, 0)],
    [(0, 0), (0, 1)],
    [(0, 0), (1, 0)],

    # --- straight lines (horizontal) ---
    [(0, 0), (0, 1), (0, 2)],
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],

    # --- straight lines (vertical) ---
    [(0, 0), (1, 0), (2, 0)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],

    # --- squares ---
    [(0, 0), (0, 1), (1, 0), (1, 1)],
    [(0, 0), (0, 1), (0, 2),
     (1, 0), (1, 1), (1, 2),
     (2, 0), (2, 1), (2, 2)],

    # --- L shapes (all 4 rotations) ---
    [(0, 0), (1, 0), (2, 0), (2, 1)],
    [(0, 0), (0, 1), (0, 2), (1, 0)],
    [(0, 0), (0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 0), (1, 1), (1, 2)],

    # --- J shapes ---
    [(0, 1), (1, 1), (2, 0), (2, 1)],
    [(0, 0), (1, 0), (1, 1), (1, 2)],
    [(0, 0), (0, 1), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (0, 2), (1, 2)],

    # --- T shapes ---
    [(0, 0), (0, 1), (0, 2), (1, 1)],
    [(0, 1), (1, 0), (1, 1), (2, 1)],
    [(0, 1), (1, 0), (1, 1), (1, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 0)],

    # --- S / Z ---
    [(0, 1), (0, 2), (1, 0), (1, 1)],
    [(0, 0), (0, 1), (1, 1), (1, 2)],

    # --- corner trios (very common in Block Blast) ---
    [(0, 0), (0, 1), (1, 0)],
    [(0, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (1, 1)],
    [(0, 1), (1, 0), (1, 1)],
]


class Piece:
    \"\"\"A draggable piece on the tray.

    Attributes:
        cells: list of (row, col) offsets that are filled.
        color: RGB tuple used to draw every cell.
        rows / cols: bounding box of the shape, handy for layout.
    \"\"\"

    def __init__(self, cells, color):
        self.cells = cells
        self.color = color
        self.rows = max(r for r, _ in cells) + 1
        self.cols = max(c for _, c in cells) + 1

    @classmethod
    def random(cls):
        \"\"\"Return a fresh piece with a random shape + neon color.\"\"\"
        return cls(random.choice(SHAPES), random.choice(NEON_COLORS))

    def size(self):
        \"\"\"How many cells the piece occupies (used for scoring).\"\"\"
        return len(self.cells)
"