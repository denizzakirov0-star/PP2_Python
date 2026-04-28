import pygame
import datetime
from tools import *

pygame.init()

screen = pygame.display.set_mode((700, 500))
canvas = pygame.Surface((700, 500))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()

colors = [
    (255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),
    (0,255,255),(255,128,0),(128,0,255),(0,128,255),(128,255,0),
    (255,255,255),(0,0,0),(120,120,120),(200,100,50),(50,200,100),
    (100,50,200),(240,240,240),(60,60,60),(180,180,0),(0,180,180),
]

buttons = [(pygame.Rect(10+(i%5)*30, 10+(i//5)*30, 25, 25), c) for i, c in enumerate(colors)]

tool = "rect"
color = (255, 0, 0)
size = 10

line_start = None
drawing = False

last_pos = None

font = pygame.font.SysFont(None, 24)
text_active = False
text_pos = (0, 0)
text_input = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: tool = "rect"
            elif event.key == pygame.K_c: tool = "circle"
            elif event.key == pygame.K_e: tool = "eraser"
            elif event.key == pygame.K_l: tool = "line"
            elif event.key == pygame.K_f: tool = "fill"
            elif event.key == pygame.K_t: tool = "text"
            elif event.key == pygame.K_p: tool = "pencil"

            elif event.unicode == '1': size = 2
            elif event.unicode == '2': size = 5
            elif event.unicode == '3': size = 10

            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                now = datetime.datetime.now()
                filename = now.strftime("paint_%Y-%m-%d_%H-%M-%S.png")
                pygame.image.save(canvas, filename)

            elif text_active:
                if event.key == pygame.K_RETURN:
                    text_surface = font.render(text_input, True, color)
                    canvas.blit(text_surface, text_pos)
                    text_active = False

                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]

                else:
                    text_input += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                for rect, col in buttons:
                    if rect.collidepoint(event.pos):
                        color = col

            elif tool == "pencil":
                drawing = True
                last_pos = event.pos

            elif event.button == 1:
                if tool == "line":
                    line_start = event.pos
                    drawing = True

                elif tool == "text":
                    text_active = True
                    text_pos = event.pos
                    text_input = ""

                else:
                    x, y = event.pos

                    if tool == "rect":
                        draw_rect(canvas, x, y, size, color)

                    elif tool == "circle":
                        draw_circle(canvas, x, y, size, color)

                    elif tool == "eraser":
                        draw_eraser(canvas, x, y, size)

                    elif tool == "fill":
                        flood_fill(canvas, x, y, color)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and tool == "line" and drawing:
                draw_line(canvas, line_start, event.pos, size, color)
                drawing = False
                line_start = None
            if event.button == 1:
                drawing = False
                last_pos = None

    screen.blit(canvas, (0, 0))

    if tool == "line" and drawing and line_start:
        pygame.draw.line(screen, color, line_start, pygame.mouse.get_pos(), size)

    if tool == "pencil" and drawing:
        current_pos = pygame.mouse.get_pos()
        if last_pos:
            draw_pencil(canvas, last_pos, current_pos, size, color)
        last_pos = current_pos

    if text_active:
        preview = font.render(text_input, True, color)
        screen.blit(preview, text_pos)

    for rect, col in buttons:
        pygame.draw.rect(screen, col, rect)
        pygame.draw.rect(screen, (0,0,0), rect, 1)

    pygame.draw.rect(screen, color, (620, 10, 40, 40))
    pygame.draw.rect(screen, (0,0,0), (620, 10, 40, 40), 2)

    pygame.display.flip()
    clock.tick(120)

pygame.quit()