
import random
import pygame
from config import (
    GRID_SIZE, CELL_SIZE, BASE_SPEED, SPEED_FLOOR, SPEED_STEP, LEVEL_UP_FOOD,
    FOOD_NORMAL, FOOD_GOLD, FOOD_POISON,
    FOOD_WEIGHTS, FOOD_TIMER,
    PU_SPEED, PU_SLOW, PU_SHIELD, PU_DURATION, PU_FIELD_TTL,
    OBSTACLE_START_LEVEL, OBSTACLES_PER_LEVEL,
)


def _random_cell(occupied: set) -> tuple[int, int]:
    """Return a random grid cell (1-indexed) that isn't occupied."""
    cells = [
        (x, y)
        for x in range(1, GRID_SIZE - 1)
        for y in range(1, GRID_SIZE - 1)
        if (x, y) not in occupied
    ]
    return random.choice(cells) if cells else (1, 1)



class Food:
    def __init__(self, kind: str, pos: tuple, timed: bool = False):
        self.kind    = kind
        self.pos     = pos
        self.timed   = timed
        self.spawn   = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        if not self.timed:
            return False
        return pygame.time.get_ticks() - self.spawn > FOOD_TIMER



class PowerUp:
    def __init__(self, kind: str, pos: tuple):
        self.kind   = kind
        self.pos    = pos
        self.spawn  = pygame.time.get_ticks()
        self.active = False          
        self.collected_at: int = 0  

    def on_field_expired(self) -> bool:
        if self.active:
            return False
        return pygame.time.get_ticks() - self.spawn > PU_FIELD_TTL

    def effect_expired(self) -> bool:
        if not self.active:
            return False
        return pygame.time.get_ticks() - self.collected_at > PU_DURATION

    def collect(self):
        self.active       = True
        self.collected_at = pygame.time.get_ticks()



class GameState:
    def __init__(self, settings: dict):
        self.settings      = settings
        self.score         = 0
        self.level         = 1
        self.food_eaten    = 0        
        self.speed         = BASE_SPEED
        self.frame_counter = 0
        self.game_over     = False
        self.shield_active = False

        mid = GRID_SIZE // 2
        self.snake = [(mid - 2, mid), (mid - 1, mid), (mid, mid)]
        self.direction = (1, 0)
        self._next_dir  = (1, 0)

        self._dir_locked = False

        self.foods: list[Food] = []

        self.powerup: PowerUp | None = None

        self.active_effect: str | None = None

        self.obstacles: set[tuple] = set()

        self._spawn_food()
        self._spawn_food(poison=True)

    def _occupied(self) -> set:
        occ = set(self.snake) | self.obstacles
        for f in self.foods:
            occ.add(f.pos)
        if self.powerup and not self.powerup.active:
            occ.add(self.powerup.pos)
        return occ


    def _spawn_food(self, poison: bool = False):
        pos = _random_cell(self._occupied())
        if poison:
            self.foods.append(Food(FOOD_POISON, pos, timed=False))
        else:
            kind   = random.choices(
                [FOOD_NORMAL, FOOD_GOLD],
                weights=[70, 30]
            )[0]
            timed  = random.random() < 0.4   # 40% chance it disappears
            self.foods.append(Food(kind, pos, timed=timed))


    def _maybe_spawn_powerup(self):
        if self.powerup is not None:
            return
        if random.random() < 0.25:   # 25% chance each food eaten
            kind = random.choice([PU_SPEED, PU_SLOW, PU_SHIELD])
            pos  = _random_cell(self._occupied())
            self.powerup = PowerUp(kind, pos)


    def generate_obstacles(self):
        if self.level < OBSTACLE_START_LEVEL:
            self.obstacles = set()
            return
        count = OBSTACLES_PER_LEVEL * (self.level - OBSTACLE_START_LEVEL + 1)
        head  = self.snake[-1]
        safe  = {(head[0]+dx, head[1]+dy)
                 for dx in range(-3, 4) for dy in range(-3, 4)}
        pool  = [
            (x, y)
            for x in range(1, GRID_SIZE - 1)
            for y in range(1, GRID_SIZE - 1)
            if (x, y) not in set(self.snake) and (x, y) not in safe
        ]
        random.shuffle(pool)
        self.obstacles = set(pool[:count])


    def set_direction(self, new_dir: tuple):
        dx, dy = self.direction
        nx, ny = new_dir
        if (nx, ny) == (-dx, -dy):
            return
        self._next_dir   = new_dir
        self._dir_locked = True


    def _apply_effect(self, kind: str):
        self.active_effect = kind
        if kind == PU_SPEED:
            self.speed = max(SPEED_FLOOR, self.speed - 3)
        elif kind == PU_SLOW:
            self.speed = min(BASE_SPEED + 5, self.speed + 4)
        elif kind == PU_SHIELD:
            self.shield_active = True

    def _remove_effect(self, kind: str):
        self.active_effect = None
        if kind == PU_SPEED:
            self.speed = max(SPEED_FLOOR, BASE_SPEED - (self.level - 1) * SPEED_STEP)
        elif kind == PU_SLOW:
            self.speed = max(SPEED_FLOOR, BASE_SPEED - (self.level - 1) * SPEED_STEP)
        elif kind == PU_SHIELD:
            self.shield_active = False


    def update(self):
        if self.game_over:
            return

        self.frame_counter += 1
        effective_speed = max(SPEED_FLOOR, self.speed)
        if self.frame_counter % effective_speed != 0:
            return   
        self.direction   = self._next_dir
        self._dir_locked = False

        hx, hy    = self.snake[-1]
        dx, dy    = self.direction
        new_head  = (hx + dx, hy + dy)

        out_of_bounds = not (1 <= new_head[0] < GRID_SIZE - 1 and
                             1 <= new_head[1] < GRID_SIZE - 1)
        hits_obstacle = new_head in self.obstacles
        hits_self     = new_head in self.snake[1:]

        if out_of_bounds or hits_obstacle or hits_self:
            if self.shield_active:
                self.shield_active = False
                self.active_effect = None
                return
            self.game_over = True
            return

        self.snake.append(new_head)
        tail = self.snake.pop(0)   
        for food in self.foods[:]:
            if food.pos == new_head:
                self.foods.remove(food)
                if food.kind == FOOD_POISON:
                    if len(self.snake) > 1:
                        self.snake.pop(0)
                    if len(self.snake) <= 1:
                        self.game_over = True
                        return
                    self._spawn_food(poison=True)
                else:
                    pts = FOOD_WEIGHTS[food.kind]
                    self.score     += pts
                    self.food_eaten += 1
                    self.snake.insert(0, tail)
                    self._spawn_food()
                    self._maybe_spawn_powerup()
                    if self.food_eaten >= LEVEL_UP_FOOD:
                        self.food_eaten = 0
                        self.level      += 1
                        self.speed       = max(
                            SPEED_FLOOR,
                            self.speed - SPEED_STEP
                        )
                        self.generate_obstacles()
                break

        self.foods = [f for f in self.foods if not f.is_expired()]
        has_normal = any(f.kind != FOOD_POISON for f in self.foods)
        if not has_normal:
            self._spawn_food()

        if self.powerup:
            if not self.powerup.active:
                if self.powerup.pos == new_head:
                    self.powerup.collect()
                    self._apply_effect(self.powerup.kind)
                elif self.powerup.on_field_expired():
                    self.powerup = None
            else:
                if self.powerup.effect_expired():
                    self._remove_effect(self.powerup.kind)
                    self.powerup = None


    def effect_remaining_ms(self) -> int:
        if self.powerup and self.powerup.active:
            elapsed = pygame.time.get_ticks() - self.powerup.collected_at
            return max(0, PU_DURATION - elapsed)
        return 0