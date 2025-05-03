import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((300, 400))
pygame.display.set_caption("Tetris-ish")

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Clear screen with black
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()