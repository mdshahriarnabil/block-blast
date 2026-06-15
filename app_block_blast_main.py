"\"\"\"Main game loop, state machine and input handling.\"\"\"

import math
import sys
import pygame

from .constants import (
    WINDOW_W, WINDOW_H, FPS, TITLE,
    BOARD_X, BOARD_Y, CELL, GRID_SIZE,
    TRAY_SLOT_W, TRAY_Y, TRAY_CELL,
    SCORE_PER_BLOCK, SCORE_PER_LINE, COMBO_BONUS, LEVEL_UP_EVERY,
    NEON_COLORS,
)
from .board import Board
from .pieces import Piece
from .ui import (
    draw_background, draw_board, draw_tray, draw_dragging, draw_hud,
    draw_menu, draw_game_over, draw_name_entry, draw_leaderboard,
    power_button_rects,
)
from .sounds import SoundFX
from .leaderboard import (
    load_highscore, save_highscore,
    load_leaderboard, add_entry, qualifies,
)


# ---------------------------------------------------------------- state ids
MENU = \"menu\"
PLAYING = \"playing\"
GAME_OVER = \"gameover\"
NAME_ENTRY = \"name\"
LEADERBOARD = \"lb\"


class Game:
    \"\"\"Owns the world state and orchestrates the main loop.\"\"\"

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.fx = SoundFX(enabled=True)

        self.state = MENU
        self.board = Board()
        self.pieces = [None, None, None]
        self.score = 0
        self.level = 1
        self.combo = 0
        self.high = load_highscore()
        self.powerups = {\"bomb\": 1, \"line\": 1, \"rainbow\": 0}
        self.active_power = None        # \"bomb\" / \"line\" / \"rainbow\" or None

        self.dragging_index = None
        self.drag_pos = (0, 0)
        self.name_buffer = \"\"
        self.new_high_pending = False

        self.flash_until = 0            # ms timestamp for line-clear flash
        self.flash_color = (255, 255, 255)
        self.t = 0.0                    # elapsed seconds (for animations)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def refill_tray(self):
        for i in range(3):
            if self.pieces[i] is None:
                self.pieces[i] = Piece.random()

    def reset_run(self):
        self.board.reset()
        self.pieces = [None, None, None]
        self.refill_tray()
        self.score = 0
        self.level = 1
        self.combo = 0
        self.powerups = {\"bomb\": 1, \"line\": 1, \"rainbow\": 0}
        self.active_power = None
        self.new_high_pending = False

    def board_cell_at(self, x, y):
        \"\"\"Convert a screen pixel to a board (row, col) or None if off-board.\"\"\"
        if not (BOARD_X <= x < BOARD_X + GRID_SIZE * CELL):
            return None
        if not (BOARD_Y <= y < BOARD_Y + GRID_SIZE * CELL):
            return None
        return (y - BOARD_Y) // CELL, (x - BOARD_X) // CELL

    def tray_piece_at(self, x, y):
        \"\"\"Return slot index (0/1/2) if (x, y) hits a tray piece, else None.\"\"\"
        if y < TRAY_Y or y > TRAY_Y + TRAY_CELL * 5:
            return None
        slot = x // TRAY_SLOT_W
        if 0 <= slot < 3 and self.pieces[slot] is not None:
            return int(slot)
        return None

    def any_piece_fits(self):
        \"\"\"If at least one tray piece can be placed somewhere → game continues.\"\"\"
        for p in self.pieces:
            if p is not None and self.board.has_any_placement(p):
                return True
        return False

    # ------------------------------------------------------------------
    # Placement & clears
    # ------------------------------------------------------------------
    def place_piece(self, slot, row, col):
        piece = self.pieces[slot]
        if piece is None or not self.board.can_place(piece, row, col):
            self.fx.play(\"invalid\")
            return False

        self.board.place(piece, row, col)
        gained = piece.size() * SCORE_PER_BLOCK
        self.pieces[slot] = None
        self.fx.play(\"place\")

        rows, cols = self.board.find_full_lines()
        line_count = len(rows) + len(cols)
        if line_count > 0:
            self.board.clear_lines(rows, cols)
            self.combo = line_count
            gained += line_count * SCORE_PER_LINE
            if line_count > 1:
                gained += (line_count - 1) * COMBO_BONUS
                self.fx.play(\"combo\")
            else:
                self.fx.play(\"clear\")
            self.flash_until = pygame.time.get_ticks() + 250
            self.flash_color = (255, 230, 70) if line_count > 1 else (0, 255, 240)
        else:
            self.combo = 0

        self.add_score(gained)

        # refill tray when all 3 pieces are spent
        if all(p is None for p in self.pieces):
            self.refill_tray()

        # game over check
        if not self.any_piece_fits():
            self.end_run()
        return True

    def add_score(self, gained):
        prev_level = self.level
        self.score += gained
        self.level = 1 + self.score // LEVEL_UP_EVERY
        if self.level > prev_level:
            # reward each level-up with a fresh power-up (rotating)
            choice = [\"bomb\", \"line\", \"rainbow\"][(self.level - 2) % 3]
            self.powerups[choice] = self.powerups.get(choice, 0) + 1
            self.fx.play(\"levelup\")

    def end_run(self):
        self.fx.play(\"gameover\")
        if self.score > self.high:
            self.high = self.score
            save_highscore(self.high)
        if qualifies(self.score):
            self.new_high_pending = True
            self.name_buffer = \"\"
            self.state = NAME_ENTRY
        else:
            self.state = GAME_OVER

    # ------------------------------------------------------------------
    # Power-ups
    # ------------------------------------------------------------------
    def use_power_on(self, row, col):
        if self.active_power is None:
            return
        if self.powerups.get(self.active_power, 0) <= 0:
            self.active_power = None
            return

        cleared = 0
        if self.active_power == \"bomb\":
            cleared = self.board.bomb(row, col)
        elif self.active_power == \"line\":
            cleared = self.board.line_blast(row, col)
        elif self.active_power == \"rainbow\":
            color = self.board.cells[row][col]
            if color is None:
                self.fx.play(\"invalid\")
                return
            cleared = self.board.rainbow(color)

        if cleared > 0:
            self.powerups[self.active_power] -= 1
            self.add_score(cleared * SCORE_PER_BLOCK)
            self.fx.play(\"power\")
            self.flash_until = pygame.time.get_ticks() + 250
            self.flash_color = (255, 130, 220)
        else:
            self.fx.play(\"invalid\")
        self.active_power = None

    def click_powerup_buttons(self, mx, my):
        rects = power_button_rects()
        names = [\"bomb\", \"line\", \"rainbow\"]
        for rect, name in zip(rects, names):
            if rect.collidepoint(mx, my):
                if self.powerups.get(name, 0) > 0:
                    self.active_power = None if self.active_power == name else name
                    self.fx.play(\"click\")
                return True
        return False

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.fx.toggle()
                return
            if self.state == MENU:
                if event.key == pygame.K_RETURN:
                    self.reset_run()
                    self.state = PLAYING
                elif event.key == pygame.K_l:
                    self.state = LEADERBOARD
                elif event.key == pygame.K_ESCAPE:
                    self.quit()
            elif self.state == GAME_OVER:
                if event.key == pygame.K_RETURN:
                    self.reset_run()
                    self.state = PLAYING
                elif event.key == pygame.K_l:
                    self.state = LEADERBOARD
                elif event.key == pygame.K_ESCAPE:
                    self.state = MENU
            elif self.state == LEADERBOARD:
                self.state = MENU if self.score == 0 else GAME_OVER
            elif self.state == NAME_ENTRY:
                if event.key == pygame.K_RETURN:
                    add_entry(self.name_buffer or \"PLAYER\",
                              self.score, self.level)
                    self.new_high_pending = False
                    self.state = GAME_OVER
                elif event.key == pygame.K_BACKSPACE:
                    self.name_buffer = self.name_buffer[:-1]
                elif event.key == pygame.K_ESCAPE:
                    add_entry(\"PLAYER\", self.score, self.level)
                    self.state = GAME_OVER
                else:
                    ch = event.unicode
                    if ch and ch.isprintable() and len(self.name_buffer) < 10:
                        self.name_buffer += ch.upper()
            elif self.state == PLAYING:
                if event.key == pygame.K_ESCAPE:
                    self.state = MENU
                elif event.key == pygame.K_1:
                    self.active_power = \"bomb\" if self.powerups[\"bomb\"] else None
                elif event.key == pygame.K_2:
                    self.active_power = \"line\" if self.powerups[\"line\"] else None
                elif event.key == pygame.K_3:
                    self.active_power = \"rainbow\" if self.powerups[\"rainbow\"] else None

        if self.state != PLAYING:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # power-up button click?
            if self.click_powerup_buttons(mx, my):
                return
            # using an active power-up on the board?
            if self.active_power is not None:
                cell = self.board_cell_at(mx, my)
                if cell is not None:
                    self.use_power_on(*cell)
                return
            # otherwise: pick up a piece from the tray
            slot = self.tray_piece_at(mx, my)
            if slot is not None:
                self.dragging_index = slot
                self.drag_pos = (mx, my)

        elif event.type == pygame.MOUSEMOTION and self.dragging_index is not None:
            self.drag_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_index is None:
                return
            piece = self.pieces[self.dragging_index]
            mx, my = event.pos
            row, col = self._anchor_from_mouse(piece, mx, my)
            if self.board.can_place(piece, row, col):
                self.place_piece(self.dragging_index, row, col)
            else:
                self.fx.play(\"invalid\")
            self.dragging_index = None

    def _anchor_from_mouse(self, piece, mx, my):
        \"\"\"Convert the cursor position to the top-left board cell of the piece.\"\"\"
        # Center the piece on the cursor in pixels, then snap to grid.
        px = mx - (piece.cols * CELL) // 2
        py = my - (piece.rows * CELL) // 2
        col = round((px - BOARD_X) / CELL)
        row = round((py - BOARD_Y) / CELL)
        return row, col

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------
    def draw(self):
        draw_background(self.screen, self.t)
        draw_hud(self.screen, self.score, self.high, self.level,
                 self.combo, self.powerups)

        ghost = None
        if self.state == PLAYING and self.dragging_index is not None:
            piece = self.pieces[self.dragging_index]
            row, col = self._anchor_from_mouse(piece, *self.drag_pos)
            valid = self.board.can_place(piece, row, col)
            ghost = (piece, row, col, valid)

        draw_board(self.screen, self.board, ghost)
        draw_tray(self.screen, self.pieces, self.dragging_index)

        # active power-up cursor hint
        if self.state == PLAYING and self.active_power is not None:
            mx, my = pygame.mouse.get_pos()
            color = {\"bomb\": (255, 80, 80),
                     \"line\": (80, 200, 255),
                     \"rainbow\": (255, 130, 220)}[self.active_power]
            pygame.draw.circle(self.screen, color, (mx, my), 18, 3)

        # dragging preview
        if self.dragging_index is not None:
            piece = self.pieces[self.dragging_index]
            draw_dragging(self.screen, piece, self.drag_pos)

        # white flash for clears
        now = pygame.time.get_ticks()
        if now < self.flash_until:
            remaining = (self.flash_until - now) / 250
            flash = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            flash.fill((*self.flash_color, int(80 * remaining)))
            self.screen.blit(flash, (0, 0))

        # overlays
        if self.state == MENU:
            draw_menu(self.screen, self.t)
        elif self.state == GAME_OVER:
            draw_game_over(self.screen, self.score, self.high,
                           self.score == self.high and self.high > 0)
        elif self.state == NAME_ENTRY:
            draw_name_entry(self.screen, self.name_buffer)
        elif self.state == LEADERBOARD:
            draw_leaderboard(self.screen, load_leaderboard())

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            self.t += 1 / FPS
            self.draw()
            self.clock.tick(FPS)

    def quit(self):
        pygame.quit()
        sys.exit(0)


def main():
    Game().run()


if __name__ == \"__main__\":
    main()
"