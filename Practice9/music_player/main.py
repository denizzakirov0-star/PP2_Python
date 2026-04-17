import pygame

pygame.init()
pygame.mixer.init()
weight, height = 1000, 600

screen = pygame.display.set_mode((weight, height))

font = pygame.font.Font(None, 50)

left = pygame.image.load("images/left.png")
left_rect = left.get_rect(topleft=(280, 330))

right = pygame.image.load("images/right.png")
right_rect = right.get_rect(topleft=(590,330))

pause = pygame.image.load("images/pause.png")
pause_playing_rect = pause.get_rect(topleft=(450,330))

playing = pygame.image.load("images/playing.png")


end = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(end)

clock = pygame.time.Clock()
p = 0
L = ["music/rickroll.wav", "music/study.wav", "music/crikets.mp3"]
i = True
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pygame.mixer.music.load(L[p])
                pygame.mixer.music.play()
                i = False
            elif event.key == pygame.K_s:
                pygame.mixer.music.pause()
                i = True
            elif event.key == pygame.K_n and p < 2:
                p += 1
                pygame.mixer.music.load(L[p])
                pygame.mixer.music.play()
                i = False
            elif event.key == pygame.K_b and p > 0:
                p -= 1
                pygame.mixer.music.load(L[p])
                pygame.mixer.music.play()
                i = False
            elif event.key == pygame.K_q:
                running = False

        if event.type == end:
            i = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pygame.mixer.music.load(L[p])
            if pause_playing_rect.collidepoint(event.pos):
                if i:
                    i = False
                    pygame.mixer.music.play()
                else:
                    i = True
                    pygame.mixer.music.pause()

            elif left_rect.collidepoint(event.pos) and p > 0:
                p -= 1
                pygame.mixer.music.load(L[p])
                pygame.mixer.music.play()
                i = False
            elif left_rect.collidepoint(event.pos):
                pygame.mixer.music.play()
                i = False

            elif right_rect.collidepoint(event.pos) and p < 2:
                p += 1
                pygame.mixer.music.load(L[p])
                pygame.mixer.music.play()
                i = False
            elif right_rect.collidepoint(event.pos):
                pygame.mixer.music.play()
                i = False
    
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (70, 102, 200), (430, 275, 150, 50), 2)
    screen.blit(left, left_rect)
    screen.blit(right, right_rect)
    if i:
        screen.blit(pause, pause_playing_rect)
    else:
        screen.blit(playing, pause_playing_rect)
    text = font.render(L[p][6:-4], True, (255, 255, 255))
    text_rect = text.get_rect(center=(505, 300))
    screen.blit(text, text_rect)
    clock.tick(60)
    pygame.display.flip()