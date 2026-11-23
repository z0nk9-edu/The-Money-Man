import pygame
import random
import math
import asyncio
import sys
import poker
from deck import Card

pygame.init()

WIDTH = 1000
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Money Man")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


def _draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


async def main():
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


asyncio.run(main())
