"\"\"\"Unit tests for the core game logic – board, pieces, leaderboard.

We deliberately avoid testing pygame rendering: the logic layer is
fully decoupled from drawing, so we can validate it without a display.
\"\"\"

import json
import os
import tempfile
import unittest
from unittest import mock

from block_blast.board import Board
from block_blast.pieces import Piece, SHAPES
from block_blast import leaderboard as lb


GREEN = (90, 255, 160)
CYAN = (0, 255, 240)
PINK = (255, 90, 130)


class BoardTests(unittest.TestCase):

    def test_empty_board(self):
        b = Board()
        self.assertTrue(b.is_empty())
        rows, cols = b.find_full_lines()
        self.assertEqual(rows, [])
        self.assertEqual(cols, [])

    def test_place_and_blocked(self):
        b = Board()
        p = Piece([(0, 0), (0, 1)], GREEN)
        self.assertTrue(b.can_place(p, 0, 0))
        b.place(p, 0, 0)
        # cells now hold the color
        self.assertEqual(b.cells[0][0], GREEN)
        self.assertEqual(b.cells[0][1], GREEN)
        # cannot place overlapping
        self.assertFalse(b.can_place(p, 0, 0))
        # out of bounds
        self.assertFalse(b.can_place(p, 0, 7))

    def test_row_clear(self):
        b = Board()
        # fill row 3 completely
        for c in range(8):
            b.cells[3][c] = CYAN
        rows, cols = b.find_full_lines()
        self.assertEqual(rows, [3])
        self.assertEqual(cols, [])
        n = b.clear_lines(rows, cols)
        self.assertEqual(n, 8)
        self.assertTrue(b.is_empty())

    def test_row_and_col_clear_combo(self):
        b = Board()
        for c in range(8):
            b.cells[2][c] = CYAN
        for r in range(8):
            b.cells[r][5] = PINK
        rows, cols = b.find_full_lines()
        self.assertEqual(rows, [2])
        self.assertEqual(cols, [5])
        n = b.clear_lines(rows, cols)
        # 8 + 8 = 16, but (2,5) is counted once
        self.assertEqual(n, 15)

    def test_bomb_clears_3x3(self):
        b = Board()
        for r in range(8):
            for c in range(8):
                b.cells[r][c] = CYAN
        cleared = b.bomb(3, 3)
        self.assertEqual(cleared, 9)
        # corners outside the 3x3 must still be filled
        self.assertEqual(b.cells[0][0], CYAN)
        self.assertIsNone(b.cells[3][3])

    def test_bomb_near_edge(self):
        b = Board()
        for r in range(8):
            for c in range(8):
                b.cells[r][c] = CYAN
        cleared = b.bomb(0, 0)  # only 4 valid cells in the 3x3 around (0,0)
        self.assertEqual(cleared, 4)

    def test_line_blast(self):
        b = Board()
        for r in range(8):
            for c in range(8):
                b.cells[r][c] = CYAN
        cleared = b.line_blast(4, 4)
        # full row + full col, shared cell counted once -> 15
        self.assertEqual(cleared, 15)

    def test_rainbow_color_bomb(self):
        b = Board()
        b.cells[0][0] = CYAN
        b.cells[1][1] = CYAN
        b.cells[2][2] = PINK
        cleared = b.rainbow(CYAN)
        self.assertEqual(cleared, 2)
        self.assertEqual(b.cells[2][2], PINK)

    def test_has_any_placement_false_when_full(self):
        b = Board()
        for r in range(8):
            for c in range(8):
                b.cells[r][c] = CYAN
        single = Piece([(0, 0)], GREEN)
        self.assertFalse(b.has_any_placement(single))

    def test_has_any_placement_true_when_empty(self):
        b = Board()
        big = Piece([(0, 0), (0, 1), (1, 0), (1, 1)], GREEN)
        self.assertTrue(b.has_any_placement(big))


class PieceTests(unittest.TestCase):

    def test_random_piece_has_valid_shape(self):
        for _ in range(50):
            p = Piece.random()
            self.assertGreater(p.size(), 0)
            self.assertGreaterEqual(p.rows, 1)
            self.assertGreaterEqual(p.cols, 1)

    def test_all_shapes_fit_on_board(self):
        b = Board()
        for shape in SHAPES:
            p = Piece(shape, CYAN)
            self.assertTrue(b.has_any_placement(p),
                            f\"shape {shape} cannot be placed on empty board\")


class LeaderboardTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.lb_path = os.path.join(self.tmp, \"lb.json\")
        self.hs_path = os.path.join(self.tmp, \"hs.json\")
        self.patcher = mock.patch.multiple(
            lb,
            LEADERBOARD_FILE=self.lb_path,
            HIGHSCORE_FILE=self.hs_path,
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_highscore_roundtrip(self):
        self.assertEqual(lb.load_highscore(), 0)
        lb.save_highscore(1234)
        self.assertEqual(lb.load_highscore(), 1234)

    def test_leaderboard_sorted_and_capped(self):
        for i in range(15):
            lb.add_entry(f\"P{i}\", i * 100, level=1 + i // 3)
        entries = lb.load_leaderboard()
        self.assertEqual(len(entries), 10)
        scores = [e[\"score\"] for e in entries]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_qualifies_when_empty(self):
        self.assertTrue(lb.qualifies(1))

    def test_qualifies_full_list(self):
        for i in range(10):
            lb.add_entry(f\"P{i}\", 100, level=1)
        self.assertFalse(lb.qualifies(50))
        self.assertTrue(lb.qualifies(101))


if __name__ == \"__main__\":
    unittest.main()
"