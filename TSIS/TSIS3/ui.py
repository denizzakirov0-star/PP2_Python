"""ui.py — all non-gameplay screens (menus, settings, leaderboard)"""
import pygame, sys
from pygame.locals import *
from persistence import load_leaderboard

# ── Palette ────────────────────────────────────────────────────────────────────
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0  )
GRAY      = (150, 150, 150)
DARK_GRAY = (60,  60,  80 )
RED       = (220, 50,  50 )
GREEN     = (50,  200, 70 )
BLUE      = (40,  90,  210)
YELLOW    = (255, 215, 0  )
ORANGE    = (255, 140, 0  )
CYAN      = (0,   210, 220)

SW, SH = 400, 600

# Available car colours (used by Settings and GameScreen)
CAR_COLORS = {
    "blue":   (50,  110, 230),
    "red":    (230, 50,  50 ),
    "green":  (50,  200, 80 ),
    "yellow": (230, 200, 20 ),
    "white":  (220, 220, 220),
}

DIFFICULTIES = ["easy", "normal", "hard"]
DIFF_COLORS  = {"easy": GREEN, "normal": BLUE, "hard": RED}


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _btn(surf, rect, text, font, color, hover=False, text_color=WHITE):
    shade = tuple(min(255, c + 35) for c in color) if hover else color
    pygame.draw.rect(surf, shade, rect, border_radius=9)
    pygame.draw.rect(surf, WHITE,  rect, 2, border_radius=9)
    lbl = font.render(text, True, text_color)
    surf.blit(lbl, lbl.get_rect(center=rect.center))


class _Base:
    def __init__(self, surf):
        self.surf  = surf
        self.clock = pygame.time.Clock()
        self.fL = pygame.font.SysFont("Verdana", 34, bold=True)
        self.fM = pygame.font.SysFont("Verdana", 22)
        self.fS = pygame.font.SysFont("Verdana", 16)

    def _bg(self, title: str):
        self.surf.fill((25, 25, 40))
        # subtle road-stripe decoration
        for y in range(0, SH, 44):
            pygame.draw.rect(self.surf, (35, 35, 55), (0, y, SW, 20))
        # title banner
        pygame.draw.rect(self.surf, (15, 15, 30), (0, 0, SW, 68))
        pygame.draw.line(self.surf, YELLOW, (0, 68), (SW, 68), 2)
        t = self.fL.render(title, True, YELLOW)
        self.surf.blit(t, t.get_rect(center=(SW // 2, 34)))

    @staticmethod
    def _quit_check(event):
        if event.type == QUIT:
            pygame.quit(); sys.exit()


# ══════════════════════════════════════════════════════════════════════════════
# Main Menu
# ══════════════════════════════════════════════════════════════════════════════
class MainMenuScreen(_Base):
    def __init__(self, surf, settings):
        super().__init__(surf)
        self.settings = settings
        self._btns = {
            "play":        pygame.Rect(100, 130, 200, 52),
            "leaderboard": pygame.Rect(100, 200, 200, 52),
            "settings":    pygame.Rect(100, 270, 200, 52),
            "quit":        pygame.Rect(100, 340, 200, 52),
        }

    def run(self) -> str:
        while True:
            mx, my = pygame.mouse.get_pos()
            self._bg("RACER")
            sub = self.fS.render("Arcade Racing  •  TSIS 3", True, GRAY)
            self.surf.blit(sub, sub.get_rect(center=(SW // 2, 100)))

            for name, rect in self._btns.items():
                color = RED if name == "quit" else BLUE
                _btn(self.surf, rect, name.replace("_", " ").title(),
                     self.fM, color, hover=rect.collidepoint(mx, my))

            pygame.display.update()
            for ev in pygame.event.get():
                self._quit_check(ev)
                if ev.type == MOUSEBUTTONDOWN:
                    for name, rect in self._btns.items():
                        if rect.collidepoint(ev.pos):
                            return name
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Username entry
# ══════════════════════════════════════════════════════════════════════════════
class UsernameScreen(_Base):
    def run(self):
        name = ""
        cursor_on = True
        tick = 0
        inp   = pygame.Rect(80, 250, 240, 46)
        ok    = pygame.Rect(120, 320, 160, 48)
        back  = pygame.Rect(120, 385, 160, 38)

        while True:
            mx, my = pygame.mouse.get_pos()
            self._bg("ENTER NAME")
            prompt = self.fM.render("Your racing name:", True, WHITE)
            self.surf.blit(prompt, prompt.get_rect(center=(SW // 2, 200)))

            # input box
            pygame.draw.rect(self.surf, WHITE, inp, border_radius=7)
            pygame.draw.rect(self.surf, CYAN,  inp, 2,  border_radius=7)
            display = name + ("|" if cursor_on else " ")
            self.surf.blit(self.fM.render(display, True, BLACK), (inp.x + 8, inp.y + 9))

            _btn(self.surf, ok,   "Start Race!", self.fM, GREEN,     hover=ok.collidepoint(mx,my))
            _btn(self.surf, back, "Back",        self.fS, DARK_GRAY, hover=back.collidepoint(mx,my))

            tick += 1
            if tick >= 30:
                cursor_on = not cursor_on; tick = 0

            pygame.display.update()
            for ev in pygame.event.get():
                self._quit_check(ev)
                if ev.type == KEYDOWN:
                    if   ev.key == K_RETURN and name.strip(): return name.strip()
                    elif ev.key == K_BACKSPACE:               name = name[:-1]
                    elif ev.key == K_ESCAPE:                  return None
                    elif len(name) < 16 and ev.unicode.isprintable():
                        name += ev.unicode
                if ev.type == MOUSEBUTTONDOWN:
                    if ok.collidepoint(ev.pos) and name.strip(): return name.strip()
                    if back.collidepoint(ev.pos):                return None
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Settings
# ══════════════════════════════════════════════════════════════════════════════
class SettingsScreen(_Base):
    def __init__(self, surf, settings):
        super().__init__(surf)
        self.s = settings.copy()

    def run(self):
        colors = list(CAR_COLORS.keys())
        ci = colors.index(self.s.get("car_color", "blue"))
        di = DIFFICULTIES.index(self.s.get("difficulty", "normal"))

        snd_btn  = pygame.Rect(220, 148, 120, 40)
        cl_btn   = pygame.Rect(58,  228,  36, 36)
        cr_btn   = pygame.Rect(306, 228,  36, 36)
        dl_btn   = pygame.Rect(58,  308,  36, 36)
        dr_btn   = pygame.Rect(306, 308,  36, 36)
        save_btn = pygame.Rect(80,  430, 240, 50)
        back_btn = pygame.Rect(80,  496, 240, 38)

        while True:
            mx, my = pygame.mouse.get_pos()
            self._bg("SETTINGS")

            # ── Sound ────────────────────────────────────────────────────────
            self.surf.blit(self.fM.render("Sound:", True, WHITE), (58, 156))
            sc = GREEN if self.s.get("sound", True) else RED
            _btn(self.surf, snd_btn, "ON" if self.s.get("sound") else "OFF",
                 self.fM, sc, hover=snd_btn.collidepoint(mx, my))

            # ── Car colour ───────────────────────────────────────────────────
            self.surf.blit(self.fM.render("Car Colour:", True, WHITE), (58, 196))
            _btn(self.surf, cl_btn, "<", self.fS, DARK_GRAY, hover=cl_btn.collidepoint(mx, my))
            _btn(self.surf, cr_btn, ">", self.fS, DARK_GRAY, hover=cr_btn.collidepoint(mx, my))
            cname = colors[ci]
            prev  = pygame.Rect(148, 226, 110, 40)
            pygame.draw.rect(self.surf, CAR_COLORS[cname], prev, border_radius=5)
            pygame.draw.rect(self.surf, WHITE, prev, 2, border_radius=5)
            tc = BLACK if cname == "white" else WHITE
            self.surf.blit(self.fS.render(cname.title(), True, tc), 
                           self.fS.render(cname.title(), True, tc).get_rect(center=prev.center))

            # ── Difficulty ───────────────────────────────────────────────────
            self.surf.blit(self.fM.render("Difficulty:", True, WHITE), (58, 276))
            _btn(self.surf, dl_btn, "<", self.fS, DARK_GRAY, hover=dl_btn.collidepoint(mx, my))
            _btn(self.surf, dr_btn, ">", self.fS, DARK_GRAY, hover=dr_btn.collidepoint(mx, my))
            dname = DIFFICULTIES[di]
            dprev = pygame.Rect(148, 306, 110, 40)
            pygame.draw.rect(self.surf, DIFF_COLORS[dname], dprev, border_radius=5)
            pygame.draw.rect(self.surf, WHITE, dprev, 2, border_radius=5)
            self.surf.blit(self.fS.render(dname.title(), True, WHITE),
                           self.fS.render(dname.title(), True, WHITE).get_rect(center=dprev.center))

            _btn(self.surf, save_btn, "Save & Back", self.fM, GREEN,     hover=save_btn.collidepoint(mx,my))
            _btn(self.surf, back_btn, "Cancel",      self.fS, DARK_GRAY, hover=back_btn.collidepoint(mx,my))

            pygame.display.update()
            for ev in pygame.event.get():
                self._quit_check(ev)
                if ev.type == KEYDOWN and ev.key == K_ESCAPE: return None
                if ev.type == MOUSEBUTTONDOWN:
                    p = ev.pos
                    if snd_btn.collidepoint(p):  self.s["sound"] = not self.s.get("sound", True)
                    elif cl_btn.collidepoint(p): ci = (ci - 1) % len(colors)
                    elif cr_btn.collidepoint(p): ci = (ci + 1) % len(colors)
                    elif dl_btn.collidepoint(p): di = (di - 1) % len(DIFFICULTIES)
                    elif dr_btn.collidepoint(p): di = (di + 1) % len(DIFFICULTIES)
                    elif save_btn.collidepoint(p):
                        self.s["car_color"]  = colors[ci]
                        self.s["difficulty"] = DIFFICULTIES[di]
                        return self.s
                    elif back_btn.collidepoint(p): return None
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Game Over
# ══════════════════════════════════════════════════════════════════════════════
class GameOverScreen(_Base):
    def __init__(self, surf, result):
        super().__init__(surf)
        self.result = result   # (score, distance, coins, username)

    def run(self) -> str:
        score, dist, coins, uname = self.result
        retry = pygame.Rect(80, 420, 240, 52)
        menu  = pygame.Rect(80, 486, 240, 40)

        while True:
            mx, my = pygame.mouse.get_pos()
            self._bg("GAME  OVER")
            lines = [
                ("Driver:",   uname,       WHITE),
                ("Score:",    str(score),  YELLOW),
                ("Distance:", f"{int(dist)} m", CYAN),
                ("Coins:",    str(coins),  ORANGE),
            ]
            for i, (label, val, col) in enumerate(lines):
                y = 110 + i * 60
                self.surf.blit(self.fS.render(label, True, GRAY),  (80,  y))
                self.surf.blit(self.fM.render(val,   True, col),   (220, y))

            _btn(self.surf, retry, "Retry",     self.fM, GREEN,     hover=retry.collidepoint(mx,my))
            _btn(self.surf, menu,  "Main Menu", self.fS, DARK_GRAY, hover=menu.collidepoint(mx,my))
            pygame.display.update()

            for ev in pygame.event.get():
                self._quit_check(ev)
                if ev.type == KEYDOWN and ev.key == K_ESCAPE: return "menu"
                if ev.type == MOUSEBUTTONDOWN:
                    if retry.collidepoint(ev.pos): return "retry"
                    if menu.collidepoint(ev.pos):  return "menu"
            self.clock.tick(60)


# ══════════════════════════════════════════════════════════════════════════════
# Leaderboard
# ══════════════════════════════════════════════════════════════════════════════
class LeaderboardScreen(_Base):
    def run(self):
        back = pygame.Rect(120, 540, 160, 44)
        entries = load_leaderboard()

        RANK_COLORS = [(255,215,0), (192,192,192), (205,127,50)]

        while True:
            mx, my = pygame.mouse.get_pos()
            self._bg("LEADERBOARD")

            # column headers
            cols = [("#", 18), ("Name", 52), ("Score", 230), ("Dist(m)", 315)]
            for txt, x in cols:
                self.surf.blit(self.fS.render(txt, True, YELLOW), (x, 80))
            pygame.draw.line(self.surf, YELLOW, (10, 103), (390, 103), 1)

            if entries:
                for i, e in enumerate(entries[:10]):
                    y    = 112 + i * 38
                    rc   = RANK_COLORS[i] if i < 3 else WHITE
                    name = e.get("name", "?")[:11]
                    self.surf.blit(self.fS.render(str(i+1),              True, rc),    (18,  y))
                    self.surf.blit(self.fS.render(name,                  True, WHITE), (52,  y))
                    self.surf.blit(self.fS.render(str(e.get("score",0)), True, WHITE), (230, y))
                    self.surf.blit(self.fS.render(str(e.get("distance",0)), True, WHITE), (315, y))
            else:
                nt = self.fM.render("No scores yet!", True, GRAY)
                self.surf.blit(nt, nt.get_rect(center=(SW//2, 300)))

            _btn(self.surf, back, "Back", self.fM, DARK_GRAY, hover=back.collidepoint(mx,my))
            pygame.display.update()

            for ev in pygame.event.get():
                self._quit_check(ev)
                if ev.type == KEYDOWN and ev.key == K_ESCAPE: return
                if ev.type == MOUSEBUTTONDOWN and back.collidepoint(ev.pos): return
            self.clock.tick(60)
