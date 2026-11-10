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


async def main():
    running = True
    poker_player = poker.PokerPlayer("Player 1", 1000)
    poker_player.receive_card(Card("A", "spades"))
    poker_player.receive_card(Card("K", "hearts"))
    poker_player2 = poker.PokerPlayer("Player 2", 1000)
    poker_player2.receive_card(Card("Q", "diamonds"))
    poker_player2.receive_card(Card("J", "clubs"))
    poker_player3 = poker.PokerPlayer("Player 3", 1000)
    poker_player3.receive_card(Card("10", "hearts"))
    poker_player3.receive_card(Card("9", "spades"))
    poker_player4 = poker.PokerPlayer("Player 4", 1000)
    poker_player4.receive_card(Card("8", "diamonds"))
    poker_player4.receive_card(Card("7", "clubs"))
    poker_game = poker.PokerGame(
        [poker_player, poker_player2, poker_player3, poker_player4]
    )
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        poker_game.draw(screen, poker_player)
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


asyncio.run(main())
