import random
import pygame
def random_cords(a):
    while True:
        n = random.randint(1, 23)
        m = random.randint(1, 23)
        if [n, m] not in a:
            return [n, m]
def shift_massive(a):
    for i in range(len(a)):
        if i != 0:
            a[i-1] = a[i].copy()
    return a
pygame.init()
score = 0
speed = 60  
weight, height = 500, 500
n = 25
font = pygame.font.SysFont("Arial", 36)
screen = pygame.display.set_mode((weight, height))
dir = [1, 0]
snake = [[1, 10], [2, 10], [3, 10]]
apple = random_cords(snake)
clock = pygame.time.Clock()
board = [(x, y) for x in range(1,24) for y in range(1,24)]
running = True
a1, s1, d1, w1 = False, False, False, False
s = 0
while running:
    for i in snake:
        i = tuple(i)
        if i not in board:
            pygame.quit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d and a1 == False:
                d1 = True
                dir[0] = 1
                dir[1] = 0
                a1, s1, w1 = False, False, False
            elif event.key == pygame.K_a and d1 == False:
                a1 = True
                dir[0] = -1
                dir[1] = 0
                d1, s1, w1 = False, False, False
            elif event.key == pygame.K_w and s1 == False:
                w1 = True
                dir[0] = 0
                dir[1] = -1
                a1, s1, d1 = False, False, False
            elif event.key == pygame.K_s and w1 == False:
                s1 = True
                dir[0] = 0
                dir[1] = 1
                a1, d1, w1 = False, False, False
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 128, 0), (20, 20, 460, 460))
    for i in snake:
        x, y = i
        pygame.draw.rect(screen, (0, 255, 0), (x*20, y*20, 20, 20))
    pygame.draw.rect(screen, (255, 0, 0), (apple[0]*20, apple[1]*20, 20, 20))
    s += 1
    if s % speed == 0:
        u, i = snake[0]
        snake = shift_massive(snake)
        snake[-1][0] += dir[0]
        snake[-1][1] += dir[1]
        if snake[-1] == apple:
            snake.insert(0, [u, i])
            apple = random_cords(snake)
            score += 1
            if speed > 10:
                speed -= 2
        snake_I = snake.copy()
        snake_I.pop()
        for i in snake_I:
            if snake[-1] == i:
                pygame.quit()
    text = font.render(str(score), True, (255, 255, 255))
    screen.blit(text, (230, 10))
    pygame.display.flip()
    clock.tick(500)