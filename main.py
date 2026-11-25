import pygame
import random
import math
import asyncio
import sys
from poker import PokerGame, PokerPlayer
from blackjack import BlackjackGame, BlackjackPlayer
import maze
from deck import Card

pygame.init()

WIDTH = 1000
HEIGHT = 800
GOAL = 200
MOVE_KEYS = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Money Man")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
chips = 100


def _draw_button(rect, text, color):
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


async def get_player_name():
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 25, 300, 50)
    color = pygame.Color("lightskyblue3")
    text = ""
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        screen.fill((0, 0, 0))
        _draw_text("Enter your name:", (WIDTH // 2 - 100, HEIGHT // 2 - 100))
        pygame.draw.rect(screen, color, input_box, 2)
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        input_box.w = max(300, text_surface.get_width() + 10)
        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)

    return text


def _human_chips(game):
    if isinstance(game, BlackjackGame):
        return game.human.chips
    if isinstance(game, PokerGame):
        return game.players[0].chips
    return chips


def _draw_text(text, pos, color=(255, 255, 255)):
    screen.blit(font.render(text, True, color), pos)


async def main():
    global chips
    name = await get_player_name()
    running = True
    current_game = None
    result = None
    poker_start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
    blackjack_start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
    next_button_rect = pygame.Rect(WIDTH - 300, HEIGHT - 50, 140, 40)
    leave_button_rect = pygame.Rect(WIDTH - 150, HEIGHT - 50, 140, 40)

    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if isinstance(current_game, BlackjackGame):
                current_game.manage_events(event)
            if (
                isinstance(current_game, maze.Maze)
                and result is None
                and event.type == pygame.KEYDOWN
                and event.key in MOVE_KEYS
            ):
                current_game.move_player(*MOVE_KEYS[event.key])

                if current_game.player.reached_home():
                    result = "You win!" if chips >= GOAL else "You lose!"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if leave_button_rect.collidepoint(event.pos):
                    if current_game is None:
                        current_game = maze.Maze(chips)
                    elif isinstance(current_game, maze.Maze):
                        if result is not None:
                            chips = 100
                            result = None
                            current_game = None
                    else:
                        chips = _human_chips(current_game)
                        current_game = None
                elif current_game is None:
                    if poker_start_rect.collidepoint(event.pos):
                        current_game = poker_start(name)
                    elif blackjack_start_rect.collidepoint(event.pos):
                        current_game = blackjack_start(name)
                        current_game.deal()
                elif next_button_rect.collidepoint(event.pos):
                    if isinstance(current_game, PokerGame):
                        if all(player.hand == [] for player in current_game.players):
                            current_game.deal()
                        else:
                            await current_game.betting_round(screen, clock)
                    if isinstance(current_game, BlackjackGame):
                        current_game.update()

        if isinstance(current_game, maze.Maze):
            chips = current_game.player.chips
            for _ in range(maze.GEN_STEPS_PER_FRAME):
                current_game.step()

            if chips == 0:
                result = "Caught by AI! You lose!"

            current_game.update_ais()

            current_game.draw(screen)
            panel_x = maze.WIDTH + 10
            _draw_text(f"${chips}", (panel_x, 20), (241, 196, 15))
            _draw_text(f"Goal: ${GOAL}", (panel_x, 55))
            if not current_game.done:
                _draw_text("Escaping...", (panel_x, 110))
            elif result is None:
                _draw_text("Get home!", (panel_x, 110))
                _draw_text("Arrows/WASD", (panel_x, 145), (150, 150, 150))
            else:
                won = chips >= GOAL
                _draw_text("Home!", (panel_x, 110))
                _draw_text(
                    result, (panel_x, 145), (46, 204, 113) if won else (231, 76, 60)
                )
                _draw_button(leave_button_rect, "Restart", (128, 0, 0))
        elif current_game is not None:
            _draw_button(next_button_rect, "Next", (0, 128, 0))
            current_game.draw(screen)
            _draw_button(leave_button_rect, "Leave", (128, 0, 0))
        else:
            _draw_text("The Casino", (WIDTH // 2 - 70, 150))
            _draw_text(
                f"You have ${chips}. Get home with ${GOAL} to win.",
                (WIDTH // 2 - 250, 200),
            )
            _draw_button(poker_start_rect, "Poker", (0, 128, 0))
            _draw_button(blackjack_start_rect, "Blackjack", (0, 128, 0))
            _draw_button(leave_button_rect, "Leave", (128, 0, 0))
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


def poker_start(name):
    player = PokerPlayer(name, chips=chips)
    ai_player_1 = PokerPlayer("AI player 1", is_human=False)
    ai_player_2 = PokerPlayer("AI player 2", is_human=False)
    players = [player, ai_player_1, ai_player_2]
    return PokerGame(players)


def blackjack_start(name):
    player = BlackjackPlayer(name, chips=chips)
    ai_player = BlackjackPlayer("AI player")
    dealer = BlackjackPlayer("Dealer")
    return BlackjackGame(player, ai_player, dealer)


asyncio.run(main())
