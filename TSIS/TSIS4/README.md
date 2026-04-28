# TSIS4 — Snake Extreme

## Requirements

```
pip install pygame psycopg2-binary
```

## Database Setup

1. Create a PostgreSQL database named `snake_game`:
   ```sql
   CREATE DATABASE snake_game;
   ```
2. Edit `config.py` to set your `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS` if needed.
3. Tables are created automatically on first run.

## Running

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| W / ↑ | Move up |
| S / ↓ | Move down |
| A / ← | Move left |
| D / → | Move right |
| ESC | Quit to menu |

## Features

- **Leaderboard** — Top 10 scores saved to PostgreSQL
- **Personal best** — Shown in HUD during gameplay
- **Poison food** (dark red) — Shortens snake by 2; game over if too short
- **Power-ups** — Speed boost (orange), Slow motion (cyan), Shield (purple ★)
- **Obstacles** — Appear from Level 3 onward
- **Settings** — Snake color, grid overlay, sound (saved to `settings.json`)
- **4 screens** — Main Menu, Gameplay, Leaderboard, Settings, Game Over

## Project Structure

```
TSIS4/
├── main.py        # Pygame screens & rendering
├── game.py        # Game logic (snake, food, power-ups, obstacles)
├── db.py          # PostgreSQL layer (psycopg2)
├── config.py      # Constants & configuration
├── settings.json  # User preferences
└── README.md
```
