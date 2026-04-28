# main.py — Pygame entry point: screens + rendering

import sys
import json
import os
import pygame

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, CELL_SIZE, FPS,
    BLACK, WHITE, DARK_GREEN, GREEN, RED, DARK_RED,
    ORANGE, PURPLE, CYAN, YELLOW, GRAY, DARK_GRAY, LIGHT_GRAY, BROWN,
    FOOD_COLORS, PU_COLORS, OBSTACLE_COLOR,
    PU_SPEED, PU_SLOW, PU_SHIELD,
)
from game import GameState
import db


SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "snake_color": [60, 200, 60],
    "grid_overlay": False,
    "sound": False,
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
                for k, v in DEFAULT_SETTINGS.items():
                    data.setdefault(k, v)
                return data
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(s: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)


def draw_text(surface, text, size, color, cx, cy, font_name="monospace"):
    font = pygame.font.SysFont(font_name, size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(cx, cy))
    surface.blit(surf, rect)
    return rect

def draw_button(surface, text, rect, hovered=False):
    color  = (80, 80, 80)  if not hovered else (130, 130, 130)
    border = WHITE         if not hovered else YELLOW
    pygame.draw.rect(surface, color,  rect, border_radius=8)
    pygame.draw.rect(surface, border, rect, 2, border_radius=8)
    draw_text(surface, text, 22, WHITE, rect.centerx, rect.centery)

def make_buttons(*labels, start_y=320, spacing=60, width=220, height=44, cx=None):
    cx = cx or WINDOW_WIDTH // 2
    buttons = {}
    for i, label in enumerate(labels):
        r = pygame.Rect(0, 0, width, height)
        r.center = (cx, start_y + i * spacing)
        buttons[label] = r
    return buttons


def screen_main_menu(surface, clock, db_ok: bool) -> tuple[str, str]:
    """Returns (action, username). action ∈ 'play' | 'leaderboard' | 'settings' | 'quit'"""
    username     = ""
    input_active = True
    error_msg    = ""

    buttons = make_buttons("Play", "Leaderboard", "Settings", "Quit", start_y=360)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", ""
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.key == pygame.K_RETURN:
                        input_active = False
                    elif len(username) < 20 and event.unicode.isprintable():
                        username += event.unicode
                if event.key == pygame.K_ESCAPE:
                    return "quit", ""
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(mx, my):
                        if label == "Play":
                            if not username.strip():
                                error_msg = "Please enter a username first!"
                            else:
                                return "play", username.strip()
                        elif label == "Leaderboard":
                            return "leaderboard", username.strip()
                        elif label == "Settings":
                            return "settings", username.strip()
                        elif label == "Quit":
                            return "quit", ""

        surface.fill((10, 20, 10))

        draw_text(surface, "SNAKE", 72, GREEN, WINDOW_WIDTH//2, 90, "monospace")
        draw_text(surface, "EXTREME", 28, YELLOW, WINDOW_WIDTH//2, 150, "monospace")

        if not db_ok:
            draw_text(surface, "DB offline — scores won't be saved", 16,
                      ORANGE, WINDOW_WIDTH//2, 190)

        draw_text(surface, "Enter username:", 20, LIGHT_GRAY, WINDOW_WIDTH//2, 230)
        ub = pygame.Rect(WINDOW_WIDTH//2 - 120, 248, 240, 40)
        col = GREEN if input_active else GRAY
        pygame.draw.rect(surface, DARK_GRAY, ub, border_radius=6)
        pygame.draw.rect(surface, col, ub, 2, border_radius=6)
        uname_surf = pygame.font.SysFont("monospace", 22, bold=True).render(
            username + ("|" if input_active and pygame.time.get_ticks() % 800 < 400 else ""),
            True, WHITE
        )
        surface.blit(uname_surf, (ub.x + 8, ub.y + 8))

        if error_msg:
            draw_text(surface, error_msg, 17, RED, WINDOW_WIDTH//2, 300)

        for label, rect in buttons.items():
            draw_button(surface, label, rect, rect.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(FPS)


def screen_leaderboard(surface, clock, db_ok: bool):
    entries = db.get_leaderboard() if db_ok else []
    back_btn = pygame.Rect(WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT - 60, 160, 40)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(mx, my):
                    return

        surface.fill((10, 20, 10))
        draw_text(surface, "LEADERBOARD", 42, YELLOW, WINDOW_WIDTH//2, 40, "monospace")

        if not db_ok:
            draw_text(surface, "Database unavailable", 22, RED, WINDOW_WIDTH//2, 100)
        elif not entries:
            draw_text(surface, "No scores yet!", 22, GRAY, WINDOW_WIDTH//2, 200)
        else:
            headers = ["#", "Player", "Score", "Lvl", "Date"]
            cols    = [30, 120, 300, 390, 460]
            y0      = 90
            hf      = pygame.font.SysFont("monospace", 16, bold=True)
            for c, h in zip(cols, headers):
                surface.blit(hf.render(h, True, YELLOW), (c, y0))
            pygame.draw.line(surface, GRAY, (20, y0+20), (WINDOW_WIDTH-20, y0+20), 1)

            rf = pygame.font.SysFont("monospace", 15)
            for i, e in enumerate(entries):
                y = y0 + 30 + i * 44
                row_color = GREEN if i == 0 else (WHITE if i < 3 else LIGHT_GRAY)
                for c, val in zip(cols, [e["rank"], e["username"], e["score"],
                                          e["level"], e["date"]]):
                    surface.blit(rf.render(str(val), True, row_color), (c, y))

        draw_button(surface, "Back", back_btn, back_btn.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(FPS)



COLOR_PRESETS = {
    "Green":  [60, 200, 60],
    "Blue":   [60, 120, 220],
    "Orange": [255, 140, 0],
    "Pink":   [220, 80, 160],
    "White":  [220, 220, 220],
}

def screen_settings(surface, clock, settings: dict) -> dict:
    back_btn   = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 70, 200, 44)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(settings)
                return settings
            if event.type == pygame.MOUSEBUTTONDOWN:
                grid_r = pygame.Rect(WINDOW_WIDTH//2 + 40, 180, 80, 34)
                if grid_r.collidepoint(mx, my):
                    settings["grid_overlay"] = not settings["grid_overlay"]
                snd_r = pygame.Rect(WINDOW_WIDTH//2 + 40, 240, 80, 34)
                if snd_r.collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]
                for i, (name, rgb) in enumerate(COLOR_PRESETS.items()):
                    cr = pygame.Rect(50 + i * 100, 330, 80, 34)
                    if cr.collidepoint(mx, my):
                        settings["snake_color"] = rgb
                if back_btn.collidepoint(mx, my):
                    save_settings(settings)
                    return settings

        surface.fill((10, 20, 10))
        draw_text(surface, "SETTINGS", 42, YELLOW, WINDOW_WIDTH//2, 50, "monospace")

        draw_text(surface, "Grid Overlay:", 22, WHITE, WINDOW_WIDTH//2 - 80, 197)
        grid_r = pygame.Rect(WINDOW_WIDTH//2 + 40, 180, 80, 34)
        col    = GREEN if settings["grid_overlay"] else GRAY
        pygame.draw.rect(surface, col, grid_r, border_radius=6)
        draw_text(surface, "ON" if settings["grid_overlay"] else "OFF",
                  18, BLACK, grid_r.centerx, grid_r.centery)

        draw_text(surface, "Sound:", 22, WHITE, WINDOW_WIDTH//2 - 80, 257)
        snd_r = pygame.Rect(WINDOW_WIDTH//2 + 40, 240, 80, 34)
        scol  = GREEN if settings["sound"] else GRAY
        pygame.draw.rect(surface, scol, snd_r, border_radius=6)
        draw_text(surface, "ON" if settings["sound"] else "OFF",
                  18, BLACK, snd_r.centerx, snd_r.centery)

        draw_text(surface, "Snake Color:", 22, WHITE, WINDOW_WIDTH//2, 300)
        for i, (name, rgb) in enumerate(COLOR_PRESETS.items()):
            cr = pygame.Rect(50 + i * 100, 330, 80, 34)
            selected = settings["snake_color"] == rgb
            pygame.draw.rect(surface, rgb, cr, border_radius=6)
            if selected:
                pygame.draw.rect(surface, WHITE, cr, 3, border_radius=6)
            draw_text(surface, name, 14, BLACK if sum(rgb) > 400 else WHITE,
                      cr.centerx, cr.centery)

        px = WINDOW_WIDTH//2
        pygame.draw.rect(surface, tuple(settings["snake_color"]),
                         pygame.Rect(px - 24, 385, 48, 24), border_radius=4)
        draw_text(surface, "preview", 14, GRAY, px, 420)

        draw_button(surface, "Save & Back", back_btn, back_btn.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(FPS)



def screen_game_over(surface, clock, score, level, personal_best, db_ok) -> str:
    """Returns 'retry' or 'menu'."""
    buttons = make_buttons("Retry", "Main Menu", start_y=400, spacing=60)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_ESCAPE:
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(mx, my):
                        return "retry" if label == "Retry" else "menu"

        surface.fill((10, 10, 5))
        draw_text(surface, "GAME OVER", 56, RED, WINDOW_WIDTH//2, 120, "monospace")
        draw_text(surface, f"Score : {score}",        26, WHITE,  WINDOW_WIDTH//2, 220)
        draw_text(surface, f"Level : {level}",        26, WHITE,  WINDOW_WIDTH//2, 260)
        draw_text(surface, f"Best  : {personal_best}",26, YELLOW, WINDOW_WIDTH//2, 300)
        if score > personal_best:
            draw_text(surface, "★ NEW PERSONAL BEST ★", 22, YELLOW, WINDOW_WIDTH//2, 340)

        for label, rect in buttons.items():
            draw_button(surface, label, rect, rect.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(FPS)



HUD_HEIGHT = 40  

def cell_to_px(gx, gy):
    """Convert grid coords to pixel top-left inside the arena."""
    return gx * CELL_SIZE, HUD_HEIGHT + gy * CELL_SIZE

def draw_game(surface, state: GameState, settings: dict, personal_best: int):
    snake_color = tuple(settings["snake_color"])

    surface.fill(BLACK)

    arena = pygame.Rect(0, HUD_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - HUD_HEIGHT)
    pygame.draw.rect(surface, DARK_GREEN, arena)

    if settings["grid_overlay"]:
        for x in range(GRID_SIZE):
            px = x * CELL_SIZE
            pygame.draw.line(surface, (30, 60, 30),
                             (px, HUD_HEIGHT), (px, WINDOW_HEIGHT), 1)
        for y in range(GRID_SIZE):
            py = HUD_HEIGHT + y * CELL_SIZE
            pygame.draw.line(surface, (30, 60, 30),
                             (0, py), (WINDOW_WIDTH, py), 1)

    border = pygame.Rect(0, HUD_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - HUD_HEIGHT)
    pygame.draw.rect(surface, GRAY, border, 3)

    for (ox, oy) in state.obstacles:
        px, py = cell_to_px(ox, oy)
        pygame.draw.rect(surface, OBSTACLE_COLOR, (px+1, py+1, CELL_SIZE-2, CELL_SIZE-2), border_radius=2)
        pygame.draw.rect(surface, BROWN,          (px+1, py+1, CELL_SIZE-2, CELL_SIZE-2), 1, border_radius=2)

    for food in state.foods:
        fx, fy = cell_to_px(*food.pos)
        color  = FOOD_COLORS[food.kind]
        pygame.draw.ellipse(surface, color, (fx+2, fy+2, CELL_SIZE-4, CELL_SIZE-4))
        if food.timed:
            elapsed  = pygame.time.get_ticks() - food.spawn
            fraction = min(1.0, elapsed / 8000)
            overlay  = pygame.Surface((CELL_SIZE-4, CELL_SIZE-4), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(fraction * 160)))
            surface.blit(overlay, (fx+2, fy+2))

    if state.powerup and not state.powerup.active:
        pu = state.powerup
        px, py = cell_to_px(*pu.pos)
        col    = PU_COLORS[pu.kind]
        pygame.draw.rect(surface, col, (px+1, py+1, CELL_SIZE-2, CELL_SIZE-2), border_radius=4)
        lbl_map = {PU_SPEED: "S", PU_SLOW: "L", PU_SHIELD: "★"}
        lbl = lbl_map.get(pu.kind, "?")
        lf  = pygame.font.SysFont("monospace", 14, bold=True)
        ls  = lf.render(lbl, True, BLACK)
        surface.blit(ls, (px+4, py+3))

    for i, (gx, gy) in enumerate(state.snake):
        px, py = cell_to_px(gx, gy)
        is_head = i == len(state.snake) - 1
        c = snake_color if not is_head else (
            min(255, snake_color[0]+40),
            min(255, snake_color[1]+40),
            min(255, snake_color[2]+40)
        )
        pygame.draw.rect(surface, c, (px+1, py+1, CELL_SIZE-2, CELL_SIZE-2), border_radius=3)
        if state.shield_active and is_head:
            pygame.draw.rect(surface, CYAN,
                             (px, py, CELL_SIZE, CELL_SIZE), 2, border_radius=3)

    hf = pygame.font.SysFont("monospace", 18, bold=True)

    surface.blit(hf.render(f"Score:{state.score}", True, WHITE), (8, 10))

    lv_surf = hf.render(f"Lvl:{state.level}", True, YELLOW)
    surface.blit(lv_surf, (WINDOW_WIDTH//2 - lv_surf.get_width()//2, 10))

    pb_surf = hf.render(f"Best:{personal_best}", True, LIGHT_GRAY)
    surface.blit(pb_surf, (WINDOW_WIDTH - pb_surf.get_width() - 8, 10))

    if state.active_effect:
        rem = state.effect_remaining_ms() // 1000
        pu_labels = {PU_SPEED: "SPEED", PU_SLOW: "SLOW", PU_SHIELD: "SHIELD"}
        pu_colors = {PU_SPEED: ORANGE, PU_SLOW: CYAN, PU_SHIELD: PURPLE}
        lbl = f"{pu_labels[state.active_effect]} {rem}s"
        ef  = pygame.font.SysFont("monospace", 15, bold=True)
        es  = ef.render(lbl, True, pu_colors.get(state.active_effect, WHITE))
        surface.blit(es, (WINDOW_WIDTH//2 - es.get_width()//2, HUD_HEIGHT + 6))



def main():
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Extreme")
    clock = pygame.time.Clock()

    settings   = load_settings()
    db_ok      = db.init_db()
    username   = ""
    player_id  = None
    personal_best = 0

    while True:
        action, username = screen_main_menu(surface, clock, db_ok)
        if action == "quit":
            break
        if action == "leaderboard":
            screen_leaderboard(surface, clock, db_ok)
            continue
        if action == "settings":
            settings = screen_settings(surface, clock, settings)
            continue

        if db_ok and username:
            player_id     = db.get_or_create_player(username)
            personal_best = db.get_personal_best(username)

        while True:
            state = GameState(settings)
            state.generate_obstacles()

            playing = True
            while playing:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP    or event.key == pygame.K_w:
                            state.set_direction((0, -1))
                        elif event.key == pygame.K_DOWN  or event.key == pygame.K_s:
                            state.set_direction((0, 1))
                        elif event.key == pygame.K_LEFT  or event.key == pygame.K_a:
                            state.set_direction((-1, 0))
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            state.set_direction((1, 0))
                        elif event.key == pygame.K_ESCAPE:
                            playing = False
                            state.game_over = True   # skip save

                state.update()
                draw_game(surface, state, settings, personal_best)
                pygame.display.flip()
                clock.tick(FPS)

                if state.game_over:
                    playing = False

            if not state.game_over:
                break

            if db_ok and player_id is not None:
                db.save_session(player_id, state.score, state.level)
                personal_best = max(personal_best, state.score)

            go_action = screen_game_over(
                surface, clock,
                state.score, state.level, personal_best, db_ok
            )
            if go_action == "retry":
                continue   
            else:
                break      

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
