import pygame
import random
import math
import asyncio
import sys
import poker
import blackjack
import maze
from deck import Card

pygame.init()

WIDTH = 1000
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Money Man")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
chips = 100
name = input("Enter your name: ")


def _draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


async def main():
    running = True
    current_game = None
    poker_start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
    blackjack_start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    next_button_rect = pygame.Rect(WIDTH - 300, HEIGHT - 50, 140, 40)
    leave_button_rect = pygame.Rect(WIDTH - 150, HEIGHT - 50, 140, 40)

    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_game is None:
                    if poker_start_rect.collidepoint(event.pos):
                        current_game = poker_start()
                    elif blackjack_start_rect.collidepoint(event.pos):
                        current_game = blackjack_start()
                    elif leave_button_rect.collidepoint(event.pos):
                        current_game = maze.MazeGenerator()
                if leave_button_rect.collidepoint(event.pos):
                    current_game = None
                if next_button_rect.collidepoint(event.pos):
                    if isinstance(current_game, poker.PokerGame):
                        if all(player.hand == [] for player in current_game.players):
                            current_game.deal()
                        else:
                            await current_game.betting_round(screen, clock)
                            current_game.draw(screen)
        if current_game is not None:
            _draw_button(next_button_rect, "Next", (0, 128, 0))
        _draw_button(leave_button_rect, "Leave", (128, 0, 0))
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


def poker_start():
    player = poker.PokerPlayer(name, chips=chips)
    ai_player_1 = poker.PokerPlayer("AI player 1", is_human=False)
    ai_player_2 = poker.PokerPlayer("AI player 2", is_human=False)
    players = [player, ai_player_1, ai_player_2]
    return poker.PokerGame(players)


def blackjack_start():
    player = blackjack.BlackjackPlayer(name, chips=chips)
    ai_player = blackjack.BlackjackPlayer("AI player")
    dealer = blackjack.BlackjackPlayer("Dealer")
    return blackjack.BlackjackGame(player, ai_player, dealer)


asyncio.run(main())
