import pygame
from datetime import datetime
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo("Asia/Almaty"))
minute = now.minute
second = now.second
print(minute, second)
pygame.init()
weight, height = 1000, 1000
screen = pygame.display.set_mode((weight, height))
clock = pygame.time.Clock()
dial = pygame.image.load("images\clock.png")
right_hand = pygame.image.load("images\mickey_hand_right.png")
left_hand = pygame.image.load("images\mickey_hand_left.png")
dial = pygame.transform.scale(dial, (1000, 1000))
right_hand = pygame.transform.scale(right_hand, (600, 150))
left_hand = pygame.transform.scale(left_hand, (600, 150))
angle = 90 - second * 6
angle2 = 90 - minute * 6
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    angle += -6
    angle2 += -1/7
    rotated_right_hand = pygame.transform.rotate(right_hand, angle)
    rotated_left_hand = pygame.transform.rotate(left_hand, angle2)
    rect = rotated_right_hand.get_rect(center = (500, 500))
    rect2 = rotated_left_hand.get_rect(center = (500, 500))
    screen.blit(dial, (0, 0))
    screen.blit(rotated_right_hand, rect)
    screen.blit(rotated_left_hand, rect2)
    pygame.draw.circle(screen, (0, 0, 0), (500, 500), 35)
    clock.tick(1)
    pygame.display.flip()