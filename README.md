"# BLOCK BLAST — Neon Arcade Edition

A modern **Block Blast** clone built with Python and Pygame. Drop tetris‑style
shapes onto an 8×8 grid, fill rows and columns to BLAST them away, chain
combos, and climb the leaderboard. Built as a Code in Place final project.

![game preview](screenshots/preview.svg)

---

## Features

- **8×8 drag‑and‑drop gameplay** with a tray of three upcoming pieces.
- **Row AND column clearing** with combo scoring and multi‑line bonuses.
- **Three power‑ups**:
  - **BOMB** — clears a 3×3 area.
  - **LINE** — clears the row + column you tap.
  - **RAINBOW** — clears every block of the chosen color.
- **Levels** that auto‑advance every 500 points and reward you with a new power‑up.
- **Persistent high score + top‑10 local leaderboard** with names.
- **Procedurally generated 8‑bit sound effects** (no audio files shipped).
- **Neon arcade visuals** — animated scanlines, glowing blocks, soft pulses.
- **Game‑over detection** — the run ends when none of your three pieces fit.

## Controls

| Action | Input |
|---|---|
| Drag piece onto the board | Left mouse button |
| Activate **Bomb** power‑up | Click the BOMB button or press **1** |
| Activate **Line** power‑up | Click the LINE button or press **2** |
| Activate **Rainbow** power‑up | Click the RAINBOW button or press **3** |
| Toggle sound | **M** |
| Start / restart | **Enter** |
| Leaderboard | **L** |
| Back to menu | **Esc** |

## Quick start

> Requires \*\*Python 3.9+\*\* and a desktop environment (Pygame needs a display).

```bash

\# 1. Clone

git clone https://github.com/<your-username>/block-blast.git

cd block-blast



\# 2. (Recommended) virtual environment

python3 -m venv .venv

source .venv/bin/activate          # on Windows:  .venv\\Scripts\\activate



\# 3. Install dependencies

pip install -r requirements.txt



\# 4. Play!

python run.py

\#  -- or --

python -m block\_blast

```

## Project structure

```

block-blast/

├── block\_blast/            # game source code (package)

│   ├── \_\_init\_\_.py

│   ├── \_\_main\_\_.py         # enables `python -m block\_blast`

│   ├── main.py             # main loop + state machine

│   ├── constants.py        # colors, sizes, tuning values

│   ├── board.py            # 8x8 grid + placement / clear logic

│   ├── pieces.py           # shape library + Piece class

│   ├── ui.py               # all drawing helpers

│   ├── sounds.py           # procedural SFX (numpy + pygame.sndarray)

│   └── leaderboard.py      # JSON leaderboard + high score

├── tests/

│   └── test\_game.py        # unit tests for board / pieces / leaderboard

├── data/                   # generated at runtime (highscore.json, leaderboard.json)

├── screenshots/            # README assets

├── run.py                  # convenience launcher

├── requirements.txt

├── LICENSE

├── README.md

└── GITHUB\_UPLOAD\_GUIDE.md  # step‑by‑step guide to publish on GitHub

```

## How the game works (for curious students)

The whole game stays beginner‑readable on purpose:

- **`board.py`** stores the grid as a 2D list. Each cell is either `None`
  (empty) or an `(R, G, B)` color tuple. That single decision keeps the
  rules tiny: `can\_place`, `find\_full\_lines`, `clear\_lines` are all just a
  few loops.
- **`pieces.py`** defines every shape as a list of `(row, col)` offsets.
  Adding new pieces is a one‑line change.
- **`main.py`** is a finite state machine: `MENU → PLAYING → NAME_ENTRY →
  GAME_OVER`(plus`LEADERBOARD`). Every event handler is gated by the
  current state, which keeps the input code from getting tangled.
- **`sounds.py`** uses `numpy` to synthesise short square / sawtooth tones
  on the fly. No audio assets means a tiny repo and zero file‑path bugs.
- **`ui.py`** is *only* drawing — never reads or writes game state. That
  separation makes it easy to restyle the visuals without breaking
  anything.

## Running the tests

```bash

python -m unittest discover -s tests -v

```

The tests don't require a display — they exercise the pure game logic
(placement, line clears, power‑ups, leaderboard persistence).

## Roadmap / ideas

- Online leaderboard
- Daily challenge seed
- Touch / mobile support (Pygame‑CE)
- Custom themes (pastel, retro pixel, mono)

## Credits

Inspired by classic Block Blast mobile games. Built with love for
**Code in Place 2026**

## License

[MIT](LICENSE) — do whatever you like, just keep the notice.
"
