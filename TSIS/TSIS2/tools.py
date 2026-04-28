import pygame
def flood_fill(surface, x, y, new_color):
    width, height = surface.get_size()
    target_color = surface.get_at((x, y))
    if target_color == new_color:
        return
    stack = [(x, y)]
    while stack:
        px, py = stack.pop()
        if px < 0 or px >= width or py < 0 or py >= height:
            continue
        if surface.get_at((px, py)) != target_color:
            continue
        surface.set_at((px, py), new_color)
        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))
def draw_rect(surface, x, y, size, color):
    pygame.draw.rect(surface, color, (x - size//2, y - size//2, size, size))
def draw_circle(surface, x, y, size, color):
    pygame.draw.circle(surface, color, (x, y), size//2)
def draw_eraser(surface, x, y, size):
    pygame.draw.circle(surface, (255,255,255), (x, y), size*2)
def draw_line(surface, start, end, size, color):
    pygame.draw.line(surface, color, start, end, size)
def draw_pencil(surface, start, end, size, color):
    pygame.draw.line(surface, color, start, end, size)