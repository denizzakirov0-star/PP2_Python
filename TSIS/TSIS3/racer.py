"""racer.py — GameScreen and all in-game entities"""
import pygame, random, sys
from pygame.locals import *
from persistence import add_score
from ui import CAR_COLORS

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
PURPLE    = (180, 50,  220)

SW, SH = 400, 600
FPS    = 60

# ── Road geometry ──────────────────────────────────────────────────────────────
ROAD_L = 40
ROAD_R = 360
LANE_W = (ROAD_R - ROAD_L) // 3
LANE_CENTERS = [ROAD_L + LANE_W * i + LANE_W // 2 for i in range(3)]

# ── Difficulty presets ─────────────────────────────────────────────────────────
DIFF = {
    "easy":   dict(base_spd=3.0, traf_ms=3200, obs_ms=5500, pu_ms=3500, max_traf=2),
    "normal": dict(base_spd=5.0, traf_ms=2000, obs_ms=3500, pu_ms=5000, max_traf=3),
    "hard":   dict(base_spd=7.5, traf_ms=1100, obs_ms=2200, pu_ms=7000, max_traf=5),
}

TRAFFIC_COLORS = [
    (220,50,50),(50,50,220),(50,180,50),(200,200,50),(180,50,180),(220,120,40)
]


# ── Asset loader ───────────────────────────────────────────────────────────────
def _load(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None


# ── Generic car drawing (fallback when no image) ───────────────────────────────
def _draw_car(surf, color, rect):
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    dark = tuple(max(0, c - 70) for c in color)
    # body + cabin
    pygame.draw.rect(surf, color,   (x,        y + h//4,     w,      h//2), border_radius=4)
    pygame.draw.rect(surf, color,   (x + w//5, y,            w*3//5, h),    border_radius=5)
    # windows
    pygame.draw.rect(surf, dark,    (x + w//5+3, y+4,        w*3//5-6, h//4), border_radius=2)
    pygame.draw.rect(surf, dark,    (x + w//5+3, y+h*11//16, w*3//5-6, h//5), border_radius=2)
    # wheels
    for wx in (x + w//6, x + w*5//6):
        for wy in (y + h//5, y + h*4//5):
            pygame.draw.circle(surf, BLACK, (wx, wy), 5)


# ══════════════════════════════════════════════════════════════════════════════
# Coin
# ══════════════════════════════════════════════════════════════════════════════
class Coin:
    _VALUES  = [1,   2,   5  ]
    _WEIGHTS = [0.6, 0.3, 0.1]
    _COLORS  = {1: YELLOW, 2: ORANGE, 5: RED}

    def __init__(self, spd):
        lane = random.choice(LANE_CENTERS)
        self.value = random.choices(self._VALUES, weights=self._WEIGHTS)[0]
        self.rect  = pygame.Rect(lane - 12, random.randint(-300, -50), 24, 24)
        self.spd   = spd
        self._font = pygame.font.SysFont("Verdana", 11, bold=True)

    def update(self): self.rect.y += self.spd

    def draw(self, surf):
        c = self._COLORS[self.value]
        cx, cy = self.rect.center
        pygame.draw.circle(surf, c,     (cx, cy), 12)
        pygame.draw.circle(surf, WHITE, (cx, cy), 12, 2)
        t = self._font.render(f"+{self.value}", True, BLACK)
        surf.blit(t, t.get_rect(center=(cx, cy)))


# ══════════════════════════════════════════════════════════════════════════════
# Traffic car
# ══════════════════════════════════════════════════════════════════════════════
class TrafficCar:
    _img_cache = {}

    def __init__(self, spd):
        self.spd   = spd
        self.color = random.choice(TRAFFIC_COLORS)
        self.rect  = pygame.Rect(
            random.choice(LANE_CENTERS) - 20,
            random.randint(-300, -80),
            40, 70,
        )
        if "enemy" not in self._img_cache:
            self._img_cache["enemy"] = _load("Enemy.png", (40, 70))
        self.img = self._img_cache["enemy"]

    def update(self): self.rect.y += self.spd

    def draw(self, surf):
        if self.img:
            surf.blit(self.img, self.rect)
        else:
            _draw_car(surf, self.color, self.rect)


# ══════════════════════════════════════════════════════════════════════════════
# Road obstacle  (oil spill, barrier, pothole)
# ══════════════════════════════════════════════════════════════════════════════
class Obstacle:
    KINDS = ["oil", "barrier", "pothole"]

    def __init__(self, spd):
        self.kind = random.choice(self.KINDS)
        lane = random.choice(LANE_CENTERS)
        if self.kind == "barrier":
            w = random.choice([LANE_W - 8, LANE_W * 2 - 8])
            self.rect = pygame.Rect(lane - w // 2, random.randint(-250, -50), w, 18)
        elif self.kind == "oil":
            self.rect = pygame.Rect(lane - 30,  random.randint(-250, -50), 60, 28)
        else:
            self.rect = pygame.Rect(lane - 14, random.randint(-250, -50), 28, 18)
        self.spd = spd

    def update(self): self.rect.y += self.spd

    def draw(self, surf):
        if self.kind == "oil":
            pygame.draw.ellipse(surf, (25,  25,  25 ), self.rect)
            pygame.draw.ellipse(surf, (80,  50,  110), self.rect.inflate(-6, -4))
            pygame.draw.arc(surf, (160, 100, 220), self.rect.inflate(-10, -6), 0.2, 2.9, 2)

        elif self.kind == "barrier":
            pygame.draw.rect(surf, ORANGE, self.rect, border_radius=4)
            pygame.draw.rect(surf, WHITE,  self.rect, 2, border_radius=4)
            # warning stripes
            clip = surf.get_clip(); surf.set_clip(self.rect)
            for i in range(0, self.rect.width + 20, 20):
                x = self.rect.x + i
                pygame.draw.rect(surf, RED, (x, self.rect.y, 10, self.rect.height))
            surf.set_clip(clip)

        else:  # pothole
            pygame.draw.ellipse(surf, (55,  35,  15), self.rect)
            pygame.draw.ellipse(surf, (35,  20,  5 ), self.rect.inflate(-8, -6))


# ══════════════════════════════════════════════════════════════════════════════
# Lane hazard zone (visual warning strip)
# ══════════════════════════════════════════════════════════════════════════════
class LaneHazard:
    def __init__(self):
        li = random.randint(0, 2)
        self.rect = pygame.Rect(
            ROAD_L + li * LANE_W,
            random.randint(-500, -150),
            LANE_W, 110,
        )
        self._s = pygame.Surface((LANE_W, 110), pygame.SRCALPHA)
        self._s.fill((255, 60, 60, 55))

    def update(self, spd): self.rect.y += spd

    def draw(self, surf):
        surf.blit(self._s, self.rect.topleft)
        for i in range(0, 110, 28):
            pygame.draw.line(surf, (255, 100, 0),
                             (self.rect.x,     self.rect.y + i),
                             (self.rect.right,  self.rect.y + i), 1)


# ══════════════════════════════════════════════════════════════════════════════
# Nitro boost strip (road event)
# ══════════════════════════════════════════════════════════════════════════════
class NitroStrip:
    def __init__(self):
        li = random.randint(0, 2)
        self.rect = pygame.Rect(ROAD_L + li * LANE_W, random.randint(-400, -100), LANE_W, 36)

    def update(self, spd): self.rect.y += spd

    def draw(self, surf):
        pygame.draw.rect(surf, (255, 200, 0), self.rect, border_radius=4)
        for i in range(3):
            y = self.rect.y + 6 + i * 11
            pygame.draw.line(surf, (255, 255, 150),
                             (self.rect.x + 8, y), (self.rect.right - 8, y), 2)
        f = pygame.font.SysFont("Verdana", 11, bold=True)
        t = f.render("NITRO", True, BLACK)
        surf.blit(t, t.get_rect(center=self.rect.center))


# ══════════════════════════════════════════════════════════════════════════════
# Speed-bump strip (road event)
# ══════════════════════════════════════════════════════════════════════════════
class SpeedBump:
    def __init__(self):
        self.rect = pygame.Rect(ROAD_L, random.randint(-400, -100), ROAD_R - ROAD_L, 18)

    def update(self, spd): self.rect.y += spd

    def draw(self, surf):
        pygame.draw.rect(surf, (100, 100, 110), self.rect, border_radius=5)
        for i in range(0, self.rect.width, 26):
            pygame.draw.rect(surf, (160,160,170),
                             (self.rect.x + i, self.rect.y + 4, 14, 10), border_radius=3)
        f = pygame.font.SysFont("Verdana", 10, bold=True)
        t = f.render("SLOW", True, WHITE)
        surf.blit(t, t.get_rect(center=self.rect.center))


# ══════════════════════════════════════════════════════════════════════════════
# Power-up collectible
# ══════════════════════════════════════════════════════════════════════════════
class PowerUp:
    TYPES    = ["nitro", "shield", "repair"]
    COLORS   = {"nitro": ORANGE, "shield": CYAN, "repair": GREEN}
    SYMBOLS  = {"nitro": "N",    "shield": "S",  "repair": "R"}
    LIFETIME = 9000   # ms before auto-expire

    def __init__(self, spd):
        self.kind       = random.choice(self.TYPES)
        lane            = random.choice(LANE_CENTERS)
        self.rect       = pygame.Rect(lane - 17, random.randint(-350, -80), 34, 34)
        self.spd        = spd
        self._born      = pygame.time.get_ticks()
        self._font      = pygame.font.SysFont("Verdana", 17, bold=True)

    def update(self): self.rect.y += self.spd
    def expired(self): return pygame.time.get_ticks() - self._born > self.LIFETIME

    def draw(self, surf):
        c = self.COLORS[self.kind]
        # pulse outline
        age  = pygame.time.get_ticks() - self._born
        glow = int(abs((age % 600) / 600 * 255 - 127))
        pygame.draw.rect(surf, (glow, glow, glow), self.rect.inflate(6, 6), border_radius=9)
        pygame.draw.rect(surf, c,     self.rect, border_radius=7)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=7)
        t = self._font.render(self.SYMBOLS[self.kind], True, WHITE)
        surf.blit(t, t.get_rect(center=self.rect.center))


# ══════════════════════════════════════════════════════════════════════════════
# GameScreen
# ══════════════════════════════════════════════════════════════════════════════
class GameScreen:
    def __init__(self, surf, settings, username):
        self.surf     = surf
        self.settings = settings
        self.username = username
        self.clock    = pygame.time.Clock()

        # fonts
        self.fH = pygame.font.SysFont("Verdana", 18, bold=True)
        self.fS = pygame.font.SysFont("Verdana", 14)
        self.fT = pygame.font.SysFont("Verdana", 48, bold=True)

        # difficulty
        d = settings.get("difficulty", "normal")
        self.cfg = DIFF[d]

        # background scrolling
        self._bg1 = _load("AnimatedStreet.png", (SW, SH))
        self._bg2 = _load("AnimatedStreet.png", (SW, SH))
        self._by1 = 0.0
        self._by2 = float(-SH)

        # player
        self.pcol  = CAR_COLORS.get(settings.get("car_color", "blue"), (50, 110, 230))
        self.pimg  = _load("Player.png", (40, 70))
        self.prect = pygame.Rect(LANE_CENTERS[1] - 20, 480, 40, 70)

        # sound
        self.crash_snd = None
        if settings.get("sound", True):
            try:    self.crash_snd = pygame.mixer.Sound("crash.wav")
            except: pass

        # game state
        self.spd     = float(self.cfg["base_spd"])
        self.score   = 0
        self.coins   = 0
        self.dist    = 0.0
        self.running = True

        # power-up state
        self.active_pu      = None   # "nitro" | "shield" | None
        self.pu_end         = 0      # pygame.time ms
        self.shield_on      = False
        self.nitro_on       = False

        # entities
        self.traffic      : list[TrafficCar]  = []
        self.obstacles    : list[Obstacle]    = []
        self.powerups     : list[PowerUp]     = []
        self.coin_list    : list[Coin]        = [Coin(self.spd), Coin(self.spd)]
        self.lane_hazards : list[LaneHazard]  = []
        self.nitro_strips : list[NitroStrip]  = []
        self.bumps        : list[SpeedBump]   = []

        now = pygame.time.get_ticks()
        self._t_traf   = now
        self._t_obs    = now
        self._t_pu     = now
        self._t_haz    = now
        self._t_nitrow = now
        self._t_bump   = now
        self._t_spdinc = now

    # ── helpers ─────────────────────────────────────────────────────────────
    @property
    def eff_spd(self):
        return self.spd * 1.9 if self.nitro_on else self.spd

    def _safe_traffic(self):
        for _ in range(12):
            lane = random.choice(LANE_CENTERS)
            r = pygame.Rect(lane - 20, random.randint(-300, -80), 40, 70)
            if not r.colliderect(self.prect):
                tc = TrafficCar(self.spd); tc.rect = r
                self.traffic.append(tc)
                return

    def _safe_obstacle(self):
        for _ in range(12):
            o = Obstacle(self.spd)
            if not o.rect.colliderect(self.prect):
                self.obstacles.append(o); return

    def _activate(self, kind: str):
        self.active_pu = kind
        now = pygame.time.get_ticks()
        if kind == "nitro":
            self.nitro_on = True
            self.pu_end   = now + 4000
            self.score   += 5
        elif kind == "shield":
            self.shield_on = True
            self.pu_end    = now + 999_999
            self.score    += 3
        elif kind == "repair":
            if self.obstacles:
                self.obstacles.pop(0)
            self.score    += 2
            self.active_pu = None   # instant

    def _check_pu_expiry(self):
        if self.active_pu == "nitro" and pygame.time.get_ticks() >= self.pu_end:
            self.nitro_on  = False
            self.active_pu = None

    # ── main loop ────────────────────────────────────────────────────────────
    def run(self):
        while self.running:
            now = pygame.time.get_ticks()
            es  = self.eff_spd

            # ── events ──────────────────────────────────────────────────────
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                    self.running = False

            # ── player movement ──────────────────────────────────────────────
            keys = pygame.key.get_pressed()
            ms = 6
            if keys[K_LEFT]  and self.prect.left   > ROAD_L + 2: self.prect.x -= ms
            if keys[K_RIGHT] and self.prect.right   < ROAD_R - 2: self.prect.x += ms
            if keys[K_UP]    and self.prect.top     > SH // 2:    self.prect.y -= ms
            if keys[K_DOWN]  and self.prect.bottom  < SH - 10:    self.prect.y += ms

            # ── speed scaling ────────────────────────────────────────────────
            if now - self._t_spdinc >= 1200:
                self.spd       += 0.06
                self._t_spdinc  = now

            self._check_pu_expiry()

            # ── distance & score ─────────────────────────────────────────────
            self.dist  += es * 0.05
            self.score  = self.coins * 10 + int(self.dist // 8)

            # ── spawning ─────────────────────────────────────────────────────
            c = self.cfg
            if now - self._t_traf > c["traf_ms"] and len(self.traffic) < c["max_traf"]:
                self._safe_traffic(); self._t_traf = now
            if now - self._t_obs  > c["obs_ms"]:
                self._safe_obstacle(); self._t_obs = now
            if now - self._t_pu   > c["pu_ms"] and len(self.powerups) < 2:
                self.powerups.append(PowerUp(self.spd)); self._t_pu = now
            if now - self._t_haz  > 7000 and len(self.lane_hazards) < 2:
                self.lane_hazards.append(LaneHazard()); self._t_haz = now
            if now - self._t_nitrow > 9000 and len(self.nitro_strips) < 1:
                self.nitro_strips.append(NitroStrip()); self._t_nitrow = now
            if now - self._t_bump > 12000 and len(self.bumps) < 1:
                self.bumps.append(SpeedBump()); self._t_bump = now

            # ── updates ──────────────────────────────────────────────────────
            for t in self.traffic:      t.spd = self.spd; t.update()
            for o in self.obstacles:    o.spd = self.spd; o.update()
            for p in self.powerups:     p.spd = self.spd; p.update()
            for coin in self.coin_list: coin.spd = es;    coin.update()
            for h in self.lane_hazards: h.update(self.spd)
            for n in self.nitro_strips: n.update(self.spd)
            for b in self.bumps:        b.update(self.spd)

            # ── cull off-screen ──────────────────────────────────────────────
            self.traffic      = [t for t in self.traffic      if t.rect.top  < SH]
            self.obstacles    = [o for o in self.obstacles    if o.rect.top  < SH]
            self.powerups     = [p for p in self.powerups     if p.rect.top  < SH and not p.expired()]
            self.lane_hazards = [h for h in self.lane_hazards if h.rect.top  < SH]
            self.nitro_strips = [n for n in self.nitro_strips if n.rect.top  < SH]
            self.bumps        = [b for b in self.bumps        if b.rect.top  < SH]
            self.coin_list    = [c for c in self.coin_list    if c.rect.top  < SH]

            # keep ≥ 2 coins on screen
            while len(self.coin_list) < 2:
                self.coin_list.append(Coin(self.spd))

            # ── collect coins ────────────────────────────────────────────────
            for coin in self.coin_list[:]:
                if self.prect.colliderect(coin.rect):
                    self.coins += coin.value
                    self.coin_list.remove(coin)

            # ── collect power-ups ────────────────────────────────────────────
            for p in self.powerups[:]:
                if self.prect.colliderect(p.rect):
                    self._activate(p.kind)
                    self.powerups.remove(p)
                    break

            # ── nitro strip (road event) ─────────────────────────────────────
            for n in self.nitro_strips[:]:
                if self.prect.colliderect(n.rect):
                    self._activate("nitro")
                    self.nitro_strips.remove(n)

            # ── speed bump (road event) ──────────────────────────────────────
            for b in self.bumps[:]:
                if self.prect.colliderect(b.rect):
                    self.spd = max(float(self.cfg["base_spd"]), self.spd * 0.65)
                    self.bumps.remove(b)

            # ── collisions ───────────────────────────────────────────────────
            dead = False

            for t in self.traffic[:]:
                if self.prect.colliderect(t.rect):
                    if self.shield_on:
                        self.shield_on = False; self.active_pu = None
                        self.traffic.remove(t)
                    else:
                        dead = True; break

            if not dead:
                for o in self.obstacles[:]:
                    if self.prect.colliderect(o.rect):
                        if o.kind == "barrier":
                            if self.shield_on:
                                self.shield_on = False; self.active_pu = None
                                self.obstacles.remove(o)
                            else:
                                dead = True; break
                        elif o.kind == "oil":
                            self.spd = max(float(self.cfg["base_spd"]), self.spd * 0.70)
                            self.obstacles.remove(o)
                        elif o.kind == "pothole":
                            self.score = max(0, self.score - 5)
                            self.obstacles.remove(o)

            if dead:
                if self.crash_snd: self.crash_snd.play()
                self._crash_flash()
                self.running = False
                break

            # ── draw ─────────────────────────────────────────────────────────
            self._draw_all()
            pygame.display.update()
            self.clock.tick(FPS)

        # save & return result
        add_score(self.username, self.score, self.dist)
        return (self.score, self.dist, self.coins, self.username)

    # ── drawing methods ──────────────────────────────────────────────────────
    def _draw_all(self):
        # background
        s = self.eff_spd
        if self._bg1:
            self._by1 += s; self._by2 += s
            if self._by1 >= SH:  self._by1 = -SH
            if self._by2 >= SH:  self._by2 = -SH
            self.surf.blit(self._bg1, (0, int(self._by1)))
            self.surf.blit(self._bg2, (0, int(self._by2)))
        else:
            self.surf.fill((28, 28, 42))

        # road
        pygame.draw.rect(self.surf, (58, 58, 62), (ROAD_L, 0, ROAD_R - ROAD_L, SH))
        pygame.draw.rect(self.surf, (200, 200, 50), (ROAD_L,   0, 5, SH))
        pygame.draw.rect(self.surf, (200, 200, 50), (ROAD_R-5, 0, 5, SH))
        offset = int(self.dist * 2.2) % 60
        for lx in [ROAD_L + LANE_W, ROAD_L + LANE_W * 2]:
            for y in range(-60 + offset, SH, 60):
                pygame.draw.rect(self.surf, WHITE, (lx - 2, y, 4, 34))

        # lane hazards behind everything
        for h in self.lane_hazards: h.draw(self.surf)

        # road events
        for n in self.nitro_strips: n.draw(self.surf)
        for b in self.bumps:        b.draw(self.surf)

        # obstacles, traffic, power-ups, coins
        for o in self.obstacles:    o.draw(self.surf)
        for t in self.traffic:      t.draw(self.surf)
        for p in self.powerups:     p.draw(self.surf)
        for c in self.coin_list:    c.draw(self.surf)

        # player
        if self.pimg:
            self.surf.blit(self.pimg, self.prect)
        else:
            _draw_car(self.surf, self.pcol, self.prect)

        # shield aura
        if self.shield_on:
            pygame.draw.rect(self.surf, CYAN, self.prect.inflate(10, 10), 3, border_radius=7)

        self._draw_hud()

    def _draw_hud(self):
        # semi-transparent bar
        bar = pygame.Surface((SW, 62), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 170))
        self.surf.blit(bar, (0, 0))

        self.surf.blit(self.fH.render(f"Score: {self.score}",       True, YELLOW), (8,  4))
        self.surf.blit(self.fH.render(f"Coins: {self.coins}",       True, ORANGE), (8, 30))
        self.surf.blit(self.fS.render(f"Dist: {int(self.dist)} m",  True, WHITE),  (220, 4))
        self.surf.blit(self.fS.render(f"Speed: {self.spd:.1f}",     True, GRAY),   (220,28))

        if self.active_pu:
            rem = max(0, (self.pu_end - pygame.time.get_ticks()) // 1000)
            col = {"nitro": ORANGE, "shield": CYAN}.get(self.active_pu, GREEN)
            label = self.active_pu.upper()
            if self.active_pu == "nitro":
                label += f"  {rem}s"
            elif self.active_pu == "shield":
                label += "  ACTIVE"
            bg = pygame.Surface((155, 58), pygame.SRCALPHA)
            bg.fill((10, 10, 10, 190))
            self.surf.blit(bg, (SW - 160, 0))
            t = self.fH.render(label, True, col)
            self.surf.blit(t, t.get_rect(center=(SW - 80, 31)))

    def _crash_flash(self):
        for _ in range(3):
            self.surf.fill((220, 40, 40))
            t = self.fT.render("CRASH!", True, WHITE)
            self.surf.blit(t, t.get_rect(center=(SW // 2, SH // 2)))
            pygame.display.update()
            pygame.time.wait(180)
            self.surf.fill((0, 0, 0))
            pygame.display.update()
            pygame.time.wait(80)
