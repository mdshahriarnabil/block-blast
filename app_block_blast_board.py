"\"\"\"The 8x8 game board plus all of its logic.

The board is a 2D list. Empty cells store ``None``, filled cells store
an RGB color tuple.  That single decision keeps placement, line-clears
and rendering nice and simple.
\"\"\"

from .constants import GRID_SIZE


class Board:
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.cells = [[None] * size for _ in range(size)]

    # ------------------------------------------------------------------
    # Placement
    # ------------------------------------------------------------------
    def can_place(self, piece, row, col):
        \"\"\"Return True if ``piece`` fits at (row, col) with no overlap.\"\"\"
        for dr, dc in piece.cells:
            r, c = row + dr, col + dc
            if r < 0 or r >= self.size or c < 0 or c >= self.size:
                return False
            if self.cells[r][c] is not None:
                return False
        return True

    def place(self, piece, row, col):
        \"\"\"Place ``piece`` on the board. Caller must check ``can_place`` first.\"\"\"
        for dr, dc in piece.cells:
            self.cells[row + dr][col + dc] = piece.color

    def has_any_placement(self, piece):
        \"\"\"Is there at least one spot where ``piece`` would fit?\"\"\"
        for r in range(self.size):
            for c in range(self.size):
                if self.can_place(piece, r, c):
                    return True
        return False

    # ------------------------------------------------------------------
    # Line clearing
    # ------------------------------------------------------------------
    def find_full_lines(self):
        \"\"\"Return (full_rows, full_cols) – lists of indices that are complete.\"\"\"
        rows = [r for r in range(self.size)
                if all(self.cells[r][c] is not None for c in range(self.size))]
        cols = [c for c in range(self.size)
                if all(self.cells[r][c] is not None for r in range(self.size))]
        return rows, cols

    def clear_lines(self, rows, cols):
        \"\"\"Wipe the given rows and columns. Returns the count of cells cleared.\"\"\"
        cleared = set()
        for r in rows:
            for c in range(self.size):
                cleared.add((r, c))
        for c in cols:
            for r in range(self.size):
                cleared.add((r, c))
        for r, c in cleared:
            self.cells[r][c] = None
        return len(cleared)

    # ------------------------------------------------------------------
    # Power-ups
    # ------------------------------------------------------------------
    def bomb(self, row, col):
        \"\"\"Clear a 3x3 area centered on (row, col). Returns cells cleared.\"\"\"
        n = 0
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if 0 <= r < self.size and 0 <= c < self.size and self.cells[r][c] is not None:
                    self.cells[r][c] = None
                    n += 1
        return n

    def line_blast(self, row, col):
        \"\"\"Clear the entire row AND column through (row, col).\"\"\"
        n = 0
        for c in range(self.size):
            if self.cells[row][c] is not None:
                self.cells[row][c] = None
                n += 1
        for r in range(self.size):
            if self.cells[r][col] is not None:
                self.cells[r][col] = None
                n += 1
        return n

    def rainbow(self, color):
        \"\"\"Remove every cell that matches ``color`` (color bomb effect).\"\"\"
        n = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.cells[r][c] == color:
                    self.cells[r][c] = None
                    n += 1
        return n

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    def reset(self):
        self.cells = [[None] * self.size for _ in range(self.size)]

    def is_empty(self):
        return all(self.cells[r][c] is None
                   for r in range(self.size) for c in range(self.size))
"