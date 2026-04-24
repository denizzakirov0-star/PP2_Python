import pygame
pygame.init()
screen = pygame.display.set_mode((700, 500))
clock = pygame.time.Clock()
colors = [
    (255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),
    (0,255,255),(255,128,0),(128,0,255),(0,128,255),(128,255,0),
    (255,255,255),(0,0,0),(120,120,120),(200,100,50),(50,200,100),
    (100,50,200),(240,240,240),(60,60,60),(180,180,0),(0,180,180),
]
size = 10
buttons = [(pygame.Rect(10+(i%5)*30, 10+(i//5)*30, 25, 25), c) for i, c in enumerate(colors)]
tool = "rect"
color = (255, 0, 0)
running = True
screen.fill((255, 255, 255))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: tool = "rect"
            elif event.key == pygame.K_c: tool = "circle"
            elif event.key == pygame.K_e: tool = "eraser"
            elif event.key == pygame.K_s: screen.fill((255,255,255))
            elif event.unicode == '+': size += 3
            elif event.unicode == '-': size -= 3
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for rect, col in buttons:
                if rect.collidepoint(event.pos):
                    color = col
    if pygame.mouse.get_pressed()[0]:
        x, y = pygame.mouse.get_pos()
        if tool == "rect":   pygame.draw.rect(screen, color, (x, y, size, size))
        elif tool == "circle": pygame.draw.circle(screen, color, (x, y), size//2)
        elif tool == "eraser": pygame.draw.circle(screen, (255,255,255), (x, y), size*2)
    for rect, col in buttons:
        pygame.draw.rect(screen, col, rect)
        pygame.draw.rect(screen, (0,0,0), rect, 1)
    pygame.draw.rect(screen, color, (620, 10, 40, 40))
    pygame.display.flip()
    clock.tick(120)
pygame.quit()