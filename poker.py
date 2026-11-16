import pygame
import asyncio
import sys


class PokerPlayer:
    def __init__(self, name, chips, is_human=True):
        self.name = name
        self.chips = chips
        self.hand = []
        self.is_human = is_human

    def receive_card(self, card):
        self.hand.append(card)

    def reset_hand(self):
        self.hand = []

    def _draw_button(self, screen, font, rect, text, color):
        pygame.draw.rect(screen, color, rect)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    async def _prompt_raise_amount(self, screen, clock, font, min_bet):
        bet_str = ""

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        bet = int(bet_str) if bet_str else 0
                        if bet > min_bet:
                            return bet
                    elif event.key == pygame.K_BACKSPACE:
                        bet_str = bet_str[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.unicode.isdigit():
                        bet_str += event.unicode

            screen.fill((0, 0, 0))
            display_bet = bet_str if bet_str else "0"
            prompt_text = f"Your bet (Min > {min_bet}): {display_bet}"
            text_surface = font.render(prompt_text, True, (255, 255, 255))
            screen.blit(text_surface, text_surface.get_rect(center=(500, 400)))

            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)

    async def prompt_bet(self, min_bet, screen, clock):
        if not self.is_human:
            return

        font = pygame.font.Font(None, 36)
        call_rect = pygame.Rect(50, 150, 140, 50)
        fold_rect = pygame.Rect(50, 220, 140, 50)
        raise_rect = pygame.Rect(50, 290, 140, 50)
        call_label = "Check" if min_bet == 0 else f"Call {min_bet} chips"

        while True:
            self._draw_button(screen, font, call_rect, call_label, (0, 128, 0))
            self._draw_button(screen, font, fold_rect, "Fold", (128, 0, 0))
            self._draw_button(screen, font, raise_rect, "Raise", (0, 128, 128))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if call_rect.collidepoint(event.pos):
                        return min_bet
                    elif fold_rect.collidepoint(event.pos):
                        return -1
                    elif raise_rect.collidepoint(event.pos):
                        raise_amount = await self._prompt_raise_amount(
                            screen, clock, font, min_bet
                        )
                        if raise_amount is not None:
                            return raise_amount

            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)

    def draw(self, screen, position):
        font = pygame.font.Font(None, 36)
        text = font.render(f"{self.name}: {self.chips} chips", True, (255, 255, 255))
        screen.blit(text, position)
        for i, card in enumerate(self.hand):
            card.draw(screen, (position[0] + i * 50, position[1] + 40))


class PokerGame:
    def __init__(self, players):
        self.players = players
        self.pot = 0
        self.current_bet = 0

    def reset_game(self, deck):
        self.pot = 0
        self.current_bet = 0
        for player in self.players:
            player.reset_hand()
        self.deal(deck)

    def deal(self, deck):
        for player in self.players:
            player.receive_card(deck.draw_card())
            player.receive_card(deck.draw_card())

    def game_loop(self):
        for i in range(len(self.players)):
            player = self.players[i]

    def draw(self, screen, player):
        player.draw(screen, (50, 50))
        font = pygame.font.Font(None, 36)
        pot_text = font.render(f"Pot: {self.pot} chips", True, (255, 255, 255))
        screen.blit(pot_text, (50, 100))
