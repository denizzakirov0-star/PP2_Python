"""persistence.py — save/load leaderboard.json and settings.json"""
import json, os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  "blue",
    "difficulty": "normal",
}


# ──────────────────────────────────────────────
# Leaderboard
# ──────────────────────────────────────────────

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_leaderboard(entries):
    entries = sorted(entries, key=lambda e: e["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(entries, f, indent=2)
    return entries


def add_score(name: str, score: int, distance: float):
    entries = load_leaderboard()
    entries.append({"name": name, "score": score, "distance": int(distance)})
    return save_leaderboard(entries)


# ──────────────────────────────────────────────
# Settings
# ──────────────────────────────────────────────

def load_settings() -> dict:
    s = DEFAULT_SETTINGS.copy()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                s.update(json.load(f))
        except Exception:
            pass
    return s


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
