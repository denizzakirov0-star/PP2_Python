import pygame, sys
from pygame.locals import *
import random, time

pygame.init()

# FPS
FPS = 60
FramePerSec = pygame.time.Clock()

# Colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)

# Screen
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5

SCORE = 0
COINS = 0

font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

background = pygame.image.load("AnimatedStreet.png")

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")

# Player
player_img = pygame.image.load("Player.png")
player_rect = player_img.get_rect()
player_rect.center = (160, 520)

# Enemy
enemy_img = pygame.image.load("Enemy.png")
enemy_rect = enemy_img.get_rect()
enemy_rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

# Coin 
coin_rect = pygame.Rect(
    random.randint(40, SCREEN_WIDTH - 40),
    random.randint(-300, -50),
    20, 20
)

# Speed increase event
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Game loop
while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == INC_SPEED:
            SPEED += 0.5

    # Background
    DISPLAYSURF.blit(background, (0, 0))

    # Score
    score_text = font_small.render(f"Score: {SCORE}", True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))

    # Coins text
    coin_text = font_small.render(f"Coins: {COINS}", True, BLACK)
    DISPLAYSURF.blit(coin_text, (280, 10))

    # Player control
    keys = pygame.key.get_pressed()
    if keys[K_LEFT] and player_rect.left > 0:
        player_rect.x -= 5
    if keys[K_RIGHT] and player_rect.right < SCREEN_WIDTH:
        player_rect.x += 5

    # Enemy movement
    enemy_rect.y += SPEED
    if enemy_rect.top > SCREEN_HEIGHT:
        SCORE += 1
        enemy_rect.x = random.randint(40, SCREEN_WIDTH - 40)
        enemy_rect.y = 0

    # Coin movement
    coin_rect.y += SPEED

    # Coin respawn if off screen
    if coin_rect.top > SCREEN_HEIGHT:
        coin_rect.x = random.randint(40, SCREEN_WIDTH - 40)
        coin_rect.y = random.randint(-300, -50)

    # Coin collect
    if player_rect.colliderect(coin_rect):
        COINS += 1
        coin_rect.x = random.randint(40, SCREEN_WIDTH - 40)
        coin_rect.y = random.randint(-300, -50)

    # Collision with enemy
    if player_rect.colliderect(enemy_rect):
        pygame.mixer.Sound('crash.wav').play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    # Draw everything
    DISPLAYSURF.blit(player_img, player_rect)
    DISPLAYSURF.blit(enemy_img, enemy_rect)

    # Draw coin
    pygame.draw.circle(DISPLAYSURF, YELLOW,
                       (coin_rect.x + 10, coin_rect.y + 10), 10)

    pygame.display.update()
    FramePerSec.tick(FPS)