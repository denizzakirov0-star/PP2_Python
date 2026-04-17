import pygame
pygame.init()
weight, height = 700, 500
screen = pygame.display.set_mode((weight, height))
clock = pygame.time.Clock()
running = True
x, y = weight//2, height//2
step = 5
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        x -= step
    elif keys[pygame.K_d]:
        x += step
    elif keys[pygame.K_w]:
        y -= step
    elif keys[pygame.K_s]:
        y += step

    x = max(25, min(675, x))
    y = max(25, min(475, y))

    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (x, y), 25)
    pygame.display.flip()
    clock.tick(60)