"""main.py — entry point; state machine connecting all screens"""
import pygame, sys
from ui      import MainMenuScreen, SettingsScreen, GameOverScreen, \
                    LeaderboardScreen, UsernameScreen
from racer   import GameScreen
from persistence import load_settings, save_settings


def main():
    pygame.init()
    surf = pygame.display.set_mode((400, 600))
    pygame.display.set_caption("Racer — TSIS 3")

    settings    = load_settings()
    state       = "menu"
    username    = "Racer"
    last_result = None

    while True:
        # ── Main menu ──────────────────────────────────────────────────────────
        if state == "menu":
            choice = MainMenuScreen(surf, settings).run()
            if   choice == "play":        state = "username"
            elif choice == "settings":    state = "settings"
            elif choice == "leaderboard": state = "leaderboard"
            elif choice == "quit":
                pygame.quit(); sys.exit()

        # ── Username entry ─────────────────────────────────────────────────────
        elif state == "username":
            name = UsernameScreen(surf).run()
            if name:
                username = name
                state    = "game"
            else:
                state = "menu"

        # ── Gameplay ───────────────────────────────────────────────────────────
        elif state == "game":
            last_result = GameScreen(surf, settings, username).run()
            state = "gameover"

        # ── Game-over screen ───────────────────────────────────────────────────
        elif state == "gameover":
            choice = GameOverScreen(surf, last_result).run()
            state  = "game" if choice == "retry" else "menu"

        # ── Settings ───────────────────────────────────────────────────────────
        elif state == "settings":
            new = SettingsScreen(surf, settings).run()
            if new is not None:
                settings = new
                save_settings(settings)
            state = "menu"

        # ── Leaderboard ────────────────────────────────────────────────────────
        elif state == "leaderboard":
            LeaderboardScreen(surf).run()
            state = "menu"


if __name__ == "__main__":
    main()
