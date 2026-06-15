"\"\"\"Game constants: sizes, colors, fonts, and tuning values.

Centralizing these makes it easy to tweak the look and feel without
hunting through the rest of the code.
\"\"\"

# ---------- Window ----------
WINDOW_W = 720
WINDOW_H = 900
FPS = 60
TITLE = \"BLOCK BLAST :: NEON ARCADE\"

# ---------- Board ----------
GRID_SIZE = 8                          # 8 x 8 board
CELL = 64                              # pixel size of one cell
BOARD_PX = GRID_SIZE * CELL            # 512 px
BOARD_X = (WINDOW_W - BOARD_PX) // 2   # centered horizontally
BOARD_Y = 150                          # below the HUD

# ---------- Tray (where the 3 next pieces live) ----------
TRAY_Y = BOARD_Y + BOARD_PX + 40
TRAY_SLOT_W = WINDOW_W // 3
TRAY_CELL = 36                         # smaller preview cells in the tray

# ---------- Colors (neon arcade palette) ----------
BG_DEEP = (8, 6, 24)                   # near-black with a violet undertone
BG_GRID = (18, 14, 42)                 # board background
GRID_LINE = (40, 30, 80)               # subtle grid lines
PANEL = (16, 12, 36)

WHITE = (240, 240, 255)
DIM = (140, 130, 180)
RED = (255, 70, 90)
GREEN = (90, 255, 160)

# Neon block colors (each piece picks one)
NEON_COLORS = [
    (0, 255, 240),     # cyan
    (255, 60, 200),    # magenta
    (255, 230, 70),    # yellow
    (120, 255, 90),    # green
    (255, 130, 60),    # orange
    (170, 100, 255),   # purple
    (255, 90, 130),    # pink
]

# Power-up cell tint
POWER_BOMB = (255, 80, 80)
POWER_LINE = (80, 200, 255)
POWER_RAINBOW = (255, 255, 255)

# ---------- Fonts ----------
FONT_NAME = \"consolas\"                 # falls back gracefully if missing
FONT_TITLE = 56
FONT_HUD = 28
FONT_SMALL = 18

# ---------- Scoring ----------
SCORE_PER_BLOCK = 1
SCORE_PER_LINE = 50
COMBO_BONUS = 25                       # extra points per line above 1
LEVEL_UP_EVERY = 500                   # score needed to advance one level

# ---------- Files ----------
LEADERBOARD_FILE = \"data/leaderboard.json\"
HIGHSCORE_FILE = \"data/highscore.json\"
MAX_LEADERBOARD = 10
"