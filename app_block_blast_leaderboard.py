"\"\"\"Local JSON-based leaderboard and high-score persistence.\"\"\"

import json
import os
from datetime import datetime

from .constants import LEADERBOARD_FILE, HIGHSCORE_FILE, MAX_LEADERBOARD


def _ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


# ---------------------------------------------------------------- high score
def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    try:
        with open(HIGHSCORE_FILE, \"r\") as f:
            return int(json.load(f).get(\"highscore\", 0))
    except (json.JSONDecodeError, ValueError, OSError):
        return 0


def save_highscore(score):
    _ensure_dir(HIGHSCORE_FILE)
    with open(HIGHSCORE_FILE, \"w\") as f:
        json.dump({\"highscore\": int(score)}, f)


# ---------------------------------------------------------------- leaderboard
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, \"r\") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_leaderboard(entries):
    _ensure_dir(LEADERBOARD_FILE)
    with open(LEADERBOARD_FILE, \"w\") as f:
        json.dump(entries, f, indent=2)


def add_entry(name, score, level):
    \"\"\"Insert a new run into the leaderboard, keeping the top N.\"\"\"
    name = (name or \"PLAYER\").strip().upper()[:10] or \"PLAYER\"
    entries = load_leaderboard()
    entries.append({
        \"name\": name,
        \"score\": int(score),
        \"level\": int(level),
        \"date\": datetime.now().strftime(\"%Y-%m-%d\"),
    })
    entries.sort(key=lambda e: e[\"score\"], reverse=True)
    entries = entries[:MAX_LEADERBOARD]
    save_leaderboard(entries)
    return entries


def qualifies(score):
    \"\"\"Does this score earn a spot on the leaderboard?\"\"\"
    entries = load_leaderboard()
    if len(entries) < MAX_LEADERBOARD:
        return True
    return score > entries[-1][\"score\"]
"