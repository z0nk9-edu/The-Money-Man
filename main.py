import pygame
import random
import math
import asyncio
import sys
import poker
from card import Card

pygame.init()

WIDTH = 1000
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Money Man")
clock = pygame.time.Clock()


async def main():
    running = True
    poker_player = poker.PokerPlayer("Player 1", 1000)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        poker_player.draw(screen, (50, 50))
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


asyncio.run(main())
