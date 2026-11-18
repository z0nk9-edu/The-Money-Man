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
    poker_player = poker.PokerPlayer("Player 1", is_human=True)
    poker_ai_1 = poker.PokerPlayer("AI Player 1", is_human=False)
    poker_ai_2 = poker.PokerPlayer("AI Player 2", is_human=False)
    poker_game = poker.PokerGame([poker_player, poker_ai_1, poker_ai_2])
    while running:
        next_button_rect = pygame.Rect(WIDTH - 150, HEIGHT - 50, 140, 40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if next_button_rect.collidepoint(event.pos):
                    if not poker_player.hand:
                        poker_game.deal()
                    else:
                        poker_game.betting_round(screen, clock)
        screen.fill((0, 0, 0))
        _draw_button(next_button_rect, "Next", (0, 128, 0))
        poker_game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


asyncio.run(main())
