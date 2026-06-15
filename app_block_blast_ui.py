"\"\"\"All drawing / rendering helpers.

Pure presentation – no game logic lives here.  Keeping rendering
separate from rules makes the code easier to read and to tweak the
visuals later.
\"\"\"

import math
import pygame

from .constants import (
    WINDOW_W, WINDOW_H, BG_DEEP, BG_GRID, GRID_LINE, PANEL,
    WHITE, DIM, GREEN, RED,
    BOARD_X, BOARD_Y, BOARD_PX, CELL, GRID_SIZE,
    TRAY_Y, TRAY_SLOT_W, TRAY_CELL,
    FONT_NAME, FONT_TITLE, FONT_HUD, FONT_SMALL,
)


# ----------------------------------------------------------------------
# Font cache
# ----------------------------------------------------------------------
_FONT_CACHE = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = pygame.font.SysFont(FONT_NAME, size, bold=bold)
        except pygame.error:
            _FONT_CACHE[key] = pygame.font.Font(None, size)
    return _FONT_CACHE[key]


def text(surface, msg, pos, size=FONT_HUD, color=WHITE, center=False, bold=False):
    surf = font(size, bold).render(str(msg), True, color)
    rect = surf.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(surf, rect)
    return rect


# ----------------------------------------------------------------------
# Background – animated neon grid
# ----------------------------------------------------------------------
def draw_background(surface, t):
    surface.fill(BG_DEEP)
    # subtle moving scanlines for arcade vibe
    for y in range(0, WINDOW_H, 4):
        a = 14 + int(6 * math.sin((y + t * 60) * 0.04))
        pygame.draw.line(surface, (a, a, a + 12), (0, y), (WINDOW_W, y))


# ----------------------------------------------------------------------
# Neon block drawing – pillowed gradient + glow
# ----------------------------------------------------------------------
def draw_block(surface, x, y, size, color, glow=True):
    \"\"\"Draw a rounded neon block at pixel coords (x, y).\"\"\"
    rect = pygame.Rect(x, y, size, size)
    if glow:
        # soft outer glow
        glow_surf = pygame.Surface((size + 16, size + 16), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*color, 60),
                         (0, 0, size + 16, size + 16), border_radius=12)
        surface.blit(glow_surf, (x - 8, y - 8))

    # main body
    pygame.draw.rect(surface, color, rect, border_radius=8)
    # inner highlight
    hl = pygame.Rect(x + 4, y + 4, size - 8, max(2, size // 3))
    light = tuple(min(255, c + 60) for c in color)
    pygame.draw.rect(surface, light, hl, border_radius=6)
    # outline
    outline = tuple(max(0, c - 80) for c in color)
    pygame.draw.rect(surface, outline, rect, width=2, border_radius=8)


# ----------------------------------------------------------------------
# Board
# ----------------------------------------------------------------------
def draw_board(surface, board, ghost=None):
    \"\"\"Draw the playfield + any filled cells.

    ``ghost`` is an optional ``(piece, row, col, valid)`` tuple shown
    semi-transparently to preview a drag.
    \"\"\"
    # board background panel with glow border
    panel = pygame.Rect(BOARD_X - 6, BOARD_Y - 6, BOARD_PX + 12, BOARD_PX + 12)
    pygame.draw.rect(surface, (60, 40, 120), panel, border_radius=14)
    pygame.draw.rect(surface, BG_GRID,
                     (BOARD_X, BOARD_Y, BOARD_PX, BOARD_PX), border_radius=10)

    # grid lines
    for i in range(GRID_SIZE + 1):
        x = BOARD_X + i * CELL
        y = BOARD_Y + i * CELL
        pygame.draw.line(surface, GRID_LINE, (x, BOARD_Y), (x, BOARD_Y + BOARD_PX))
        pygame.draw.line(surface, GRID_LINE, (BOARD_X, y), (BOARD_X + BOARD_PX, y))

    # filled cells
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            color = board.cells[r][c]
            if color is not None:
                draw_block(surface,
                           BOARD_X + c * CELL + 2, BOARD_Y + r * CELL + 2,
                           CELL - 4, color)

    # ghost preview
    if ghost is not None:
        piece, row, col, valid = ghost
        tint = (90, 255, 160) if valid else (255, 70, 90)
        for dr, dc in piece.cells:
            r, c = row + dr, col + dc
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                gs = pygame.Surface((CELL - 4, CELL - 4), pygame.SRCALPHA)
                gs.fill((*tint, 110))
                surface.blit(gs, (BOARD_X + c * CELL + 2, BOARD_Y + r * CELL + 2))


# ----------------------------------------------------------------------
# Tray + dragging piece
# ----------------------------------------------------------------------
def tray_origin(slot):
    \"\"\"Top-left pixel of slot 0/1/2 in the tray.\"\"\"
    return slot * TRAY_SLOT_W, TRAY_Y


def draw_tray(surface, pieces, dragging_index):
    pygame.draw.rect(surface, PANEL,
                     (12, TRAY_Y - 12, WINDOW_W - 24, TRAY_CELL * 5 + 24),
                     border_radius=12)
    for i, piece in enumerate(pieces):
        if piece is None or i == dragging_index:
            continue
        ox, oy = tray_origin(i)
        # center the piece inside its slot
        px = ox + (TRAY_SLOT_W - piece.cols * TRAY_CELL) // 2
        py = oy + (TRAY_CELL * 5 - piece.rows * TRAY_CELL) // 2
        for dr, dc in piece.cells:
            draw_block(surface,
                       px + dc * TRAY_CELL + 2, py + dr * TRAY_CELL + 2,
                       TRAY_CELL - 4, piece.color, glow=False)


def draw_dragging(surface, piece, mouse_pos):
    \"\"\"Draw the piece following the cursor at board scale.\"\"\"
    mx, my = mouse_pos
    # anchor so the piece is centered on the cursor
    px = mx - (piece.cols * CELL) // 2
    py = my - (piece.rows * CELL) // 2
    for dr, dc in piece.cells:
        draw_block(surface,
                   px + dc * CELL + 2, py + dr * CELL + 2,
                   CELL - 4, piece.color)


# ----------------------------------------------------------------------
# HUD: score / high / level / power-ups
# ----------------------------------------------------------------------
def draw_hud(surface, score, high, level, combo, powerups):
    # title
    text(surface, \"BLOCK BLAST\",
         (WINDOW_W // 2, 40), FONT_TITLE, (0, 255, 240),
         center=True, bold=True)
    text(surface, \"neon arcade\", (WINDOW_W // 2, 78),
         FONT_SMALL, (255, 60, 200), center=True)

    # score line
    text(surface, f\"SCORE  {score:>6}\", (24, 110), FONT_HUD, WHITE)
    text(surface, f\"HIGH  {high:>6}\", (WINDOW_W - 220, 110), FONT_HUD,
         (255, 230, 70))
    text(surface, f\"LV {level}\", (WINDOW_W // 2, 110), FONT_HUD,
         (120, 255, 90), center=True, bold=True)

    if combo > 1:
        text(surface, f\"x{combo}  COMBO!\",
             (WINDOW_W // 2, BOARD_Y - 20), FONT_HUD,
             (255, 230, 70), center=True, bold=True)

    # power-up buttons across the bottom
    draw_powerups(surface, powerups)


def power_button_rects():
    \"\"\"Return three rects for the bomb / line / rainbow buttons.\"\"\"
    y = WINDOW_H - 70
    w, h, gap = 200, 54, 12
    total = w * 3 + gap * 2
    start = (WINDOW_W - total) // 2
    return [pygame.Rect(start + i * (w + gap), y, w, h) for i in range(3)]


def draw_powerups(surface, powerups):
    rects = power_button_rects()
    labels = [
        (\"BOMB\", (255, 80, 80), powerups.get(\"bomb\", 0)),
        (\"LINE\", (80, 200, 255), powerups.get(\"line\", 0)),
        (\"RAINBOW\", (255, 130, 220), powerups.get(\"rainbow\", 0)),
    ]
    for rect, (label, color, count) in zip(rects, labels):
        active = count > 0
        bg = (30, 24, 60) if active else (20, 18, 40)
        pygame.draw.rect(surface, bg, rect, border_radius=12)
        border = color if active else DIM
        pygame.draw.rect(surface, border, rect, width=2, border_radius=12)
        text(surface, label, rect.center, FONT_HUD,
             color if active else DIM, center=True, bold=True)
        text(surface, f\"x{count}\",
             (rect.right - 14, rect.top + 6), FONT_SMALL,
             color if active else DIM)


# ----------------------------------------------------------------------
# Overlays: menu, name entry, game-over, leaderboard
# ----------------------------------------------------------------------
def dim_overlay(surface, alpha=180):
    o = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    o.fill((0, 0, 0, alpha))
    surface.blit(o, (0, 0))


def draw_menu(surface, t):
    dim_overlay(surface, 200)
    bob = math.sin(t * 2) * 6
    text(surface, \"BLOCK BLAST\",
         (WINDOW_W // 2, 220 + bob), FONT_TITLE + 12, (0, 255, 240),
         center=True, bold=True)
    text(surface, \"NEON ARCADE EDITION\",
         (WINDOW_W // 2, 280 + bob), FONT_HUD, (255, 60, 200), center=True)

    items = [
        \"PRESS  ENTER  TO  PLAY\",
        \"L  -  LEADERBOARD\",
        \"M  -  SOUND ON / OFF\",
        \"ESC  -  QUIT\",
    ]
    for i, m in enumerate(items):
        text(surface, m, (WINDOW_W // 2, 420 + i * 50), FONT_HUD,
             WHITE if i == 0 else DIM, center=True, bold=(i == 0))

    text(surface, \"drag pieces onto the 8x8 board\",
         (WINDOW_W // 2, 720), FONT_SMALL, DIM, center=True)
    text(surface, \"fill a row OR a column to BLAST it!\",
         (WINDOW_W // 2, 744), FONT_SMALL, DIM, center=True)


def draw_game_over(surface, score, high, new_high):
    dim_overlay(surface, 200)
    text(surface, \"GAME  OVER\",
         (WINDOW_W // 2, 260), FONT_TITLE, (255, 70, 90),
         center=True, bold=True)
    text(surface, f\"FINAL SCORE  {score}\",
         (WINDOW_W // 2, 360), FONT_HUD, WHITE, center=True)
    text(surface, f\"HIGH SCORE  {high}\",
         (WINDOW_W // 2, 400), FONT_HUD, (255, 230, 70), center=True)
    if new_high:
        text(surface, \"NEW  HIGH  SCORE!\",
             (WINDOW_W // 2, 450), FONT_HUD, GREEN, center=True, bold=True)
    text(surface, \"ENTER - play again    L - leaderboard    ESC - menu\",
         (WINDOW_W // 2, 540), FONT_SMALL, DIM, center=True)


def draw_name_entry(surface, current_name):
    dim_overlay(surface, 200)
    text(surface, \"NEW  HIGH  SCORE!\",
         (WINDOW_W // 2, 280), FONT_TITLE, (255, 230, 70),
         center=True, bold=True)
    text(surface, \"Enter your name:\",
         (WINDOW_W // 2, 360), FONT_HUD, WHITE, center=True)
    box = pygame.Rect(WINDOW_W // 2 - 160, 410, 320, 60)
    pygame.draw.rect(surface, (24, 18, 50), box, border_radius=10)
    pygame.draw.rect(surface, (0, 255, 240), box, width=2, border_radius=10)
    text(surface, current_name + \"_\",
         box.center, FONT_HUD, WHITE, center=True, bold=True)
    text(surface, \"press ENTER when done\",
         (WINDOW_W // 2, 500), FONT_SMALL, DIM, center=True)


def draw_leaderboard(surface, entries):
    dim_overlay(surface, 210)
    text(surface, \"LEADERBOARD\",
         (WINDOW_W // 2, 90), FONT_TITLE, (255, 60, 200),
         center=True, bold=True)
    if not entries:
        text(surface, \"no scores yet - go play!\",
             (WINDOW_W // 2, 400), FONT_HUD, DIM, center=True)
    else:
        for i, e in enumerate(entries):
            y = 180 + i * 50
            color = (255, 230, 70) if i == 0 else WHITE
            text(surface, f\"{i+1:>2}.\", (140, y), FONT_HUD, color, bold=True)
            text(surface, e[\"name\"], (200, y), FONT_HUD, color)
            text(surface, str(e[\"score\"]),
                 (WINDOW_W - 260, y), FONT_HUD, color, bold=True)
            text(surface, f\"LV{e['level']}\",
                 (WINDOW_W - 160, y), FONT_SMALL, DIM)
    text(surface, \"press any key to return\",
         (WINDOW_W // 2, WINDOW_H - 40), FONT_SMALL, DIM, center=True)
"