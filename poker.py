import pygame
import asyncio
import sys
from itertools import combinations
from collections import Counter
from deck import Card, Deck


class PokerPlayer:
    def __init__(self, name, chips=100, is_human=True):
        self.name = name
        self.chips = chips
        self.hand = []
        self.is_human = is_human
        self.font = pygame.font.Font(None, 36)

    def receive_card(self, card):
        card.hidden = not self.is_human
        self.hand.append(card)

    def reset_hand(self):
        self.hand = []

    def _draw_button(self, screen, rect, text, color):
        pygame.draw.rect(screen, color, rect)
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    async def _prompt_raise_amount(self, screen, clock, min_bet):
        bet_str = ""

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        bet = int(bet_str) if bet_str else 0
                        if bet > min_bet and bet <= self.chips:
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
            text_surface = self.font.render(prompt_text, True, (255, 255, 255))
            screen.blit(text_surface, text_surface.get_rect(center=(500, 400)))

            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)

    async def prompt_bet(self, min_bet, community_cards, screen, clock):
        if not self.is_human:
            bet = self.ai_bet(min_bet, community_cards)
            if bet == -1:
                self.chips -= bet
            return bet
        if self.chips == 0:
            return 0

        call_rect = pygame.Rect(50, 150, 140, 50)
        fold_rect = pygame.Rect(50, 220, 140, 50)
        raise_rect = pygame.Rect(50, 290, 140, 50)
        call_label = "Check" if min_bet == 0 else f"Call {min_bet} chips"

        while True:
            self._draw_button(screen, call_rect, call_label, (0, 128, 0))
            self._draw_button(screen, fold_rect, "Fold", (128, 0, 0))
            self._draw_button(screen, raise_rect, "Raise", (0, 128, 128))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if call_rect.collidepoint(event.pos):
                        if min_bet <= self.chips:
                            self.chips -= min_bet
                            return min_bet
                        else:
                            prompt_text = "Not enough chips to call. All in."
                            text_surface = self.font.render(
                                prompt_text, True, (255, 255, 255)
                            )
                            screen.blit(
                                text_surface, text_surface.get_rect(center=(500, 400))
                            )
                            return self.chips
                    elif fold_rect.collidepoint(event.pos):
                        return -1
                    elif raise_rect.collidepoint(event.pos):
                        raise_amount = None
                        while raise_amount is None:
                            raise_amount = await self._prompt_raise_amount(
                                screen, clock, min_bet
                            )
                        self.chips -= raise_amount
                        return raise_amount

            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)

    def ai_bet(self, min_bet, community_cards):
        if community_cards:
            all_cards = self.hand + community_cards
            best_score = None
            for combo in combinations(all_cards, 5):
                score = score_five_card_hand(combo)
                if best_score is None or score > best_score:
                    best_score = score
            if best_score[0] >= 3 and self.chips > min_bet:
                return min_bet * 1.5 if self.chips > min_bet * 1.5 else min_bet
            elif (
                best_score[0] >= 1
                and self.chips > min_bet
                and min_bet < self.chips // 3
            ):
                return min_bet
            else:
                return -1
        if min_bet < self.chips / 10:
            return min_bet
        else:
            return -1

    def draw(self, screen, position):
        text = self.font.render(
            f"{self.name}: {self.chips} chips", True, (255, 255, 255)
        )
        screen.blit(text, position)
        for i, card in enumerate(self.hand):
            card.draw(screen, (position[0] + i * 50, position[1] + 40))


class PokerGame:
    def __init__(self, players):
        self.players = players
        self.current_players = players.copy()
        self.pot = 0
        self.current_bet = 0
        self.community_cards = []
        self.deck = Deck()
        self.font = pygame.font.Font(None, 36)

    def add_card(self, card):
        self.deck.add_card(card)

    def reset_game(self):
        self.pot = 0
        self.current_bet = 0
        self.current_players = self.players.copy()
        self.community_cards = []
        for player in self.current_players:
            player.reset_hand()
        self.deck = Deck()

    def deal(self):
        for player in self.current_players:
            player.receive_card(self.deck.draw_card())
            player.receive_card(self.deck.draw_card())

    async def betting_round(self, screen, clock):
        player_bets = dict.fromkeys(self.current_players, 0)

        if len(self.community_cards) == 0:
            self.community_cards.extend(
                [self.deck.draw_card(), self.deck.draw_card(), self.deck.draw_card()]
            )
        elif len(self.community_cards) < 5:
            self.community_cards.append(self.deck.draw_card())

        index = 0

        while True:
            player = self.current_players[index % len(self.current_players)]

            call_amount = self.current_bet - player_bets[player]
            bet = await player.prompt_bet(
                call_amount, self.community_cards, screen, clock
            )

            if bet == -1:
                self.current_players.remove(player)
                player_bets.pop(player)
                player.reset_hand()
            else:
                new_total_bet = player_bets[player] + bet

                if new_total_bet > self.current_bet:
                    self.current_bet = new_total_bet

                self.pot += bet
                player_bets[player] = new_total_bet

            index += 1
            if len(self.current_players) > 1 and set(player_bets.values()) != {
                self.current_bet
            }:
                continue
            else:
                break

        if len(self.community_cards) == 5:
            self.win_screen(screen, clock)

    def win_screen(self, screen, clock):
        winners, score = self.evaluate_best_hand(
            self.current_players, self.community_cards
        )
        for winner in winners:
            winner.chips += self.pot // len(winners)
        winner_names = ", ".join([winner.name for winner in winners])
        prompt_text = f"Winner(s): {winner_names} with score: {score} earned {self.pot // len(self.current_players)} chips!"
        text_surface = self.font.render(prompt_text, True, (255, 255, 255))
        screen.blit(text_surface, text_surface.get_rect(center=(500, 400)))
        pygame.display.flip()
        clock.tick(1)
        self.reset_game()

    def evaluate_best_hand(self, players, community_cards):
        player_best_scores = {}

        for player in players:
            all_cards = player.hand + community_cards
            best_score = None

            for combo in combinations(all_cards, 5):
                score = score_five_card_hand(combo)
                if best_score is None or score > best_score:
                    best_score = score
            player_best_scores[player] = best_score

        max_score = max(player_best_scores.values())

        winners = [
            player for player, score in player_best_scores.items() if score == max_score
        ]
        return winners, max_score

    def draw(self, screen):
        import math

        screen_width, screen_height = screen.get_size()
        center_x = screen_width // 2
        center_y = screen_height // 2

        radius = 200

        total_players = len(self.current_players)

        for i, player in enumerate(self.current_players):
            angle = (i * 2 * math.pi) / total_players

            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))

            player.draw(screen, (x, y))
        for i, card in enumerate(self.community_cards):
            card.draw(screen, (center_x - 150 + i * 50, center_y - 75))
        pot_text = self.font.render(f"Pot: {self.pot} chips", True, (255, 255, 255))
        screen.blit(pot_text, (50, 100))


def score_five_card_hand(cards):
    ranks = sorted([c.rank_value() for c in cards], reverse=True)
    suits = [c.suit for c in cards]

    is_flush = len(set(suits)) == 1

    is_straight = False
    unique_ranks = sorted(set(ranks), reverse=True)
    if len(unique_ranks) == 5:
        if unique_ranks[0] - unique_ranks[4] == 4:
            is_straight = True
            straight_high = unique_ranks[0]
        elif unique_ranks == [14, 5, 4, 3, 2]:
            is_straight = True
            ranks = [5, 4, 3, 2, 1]
            straight_high = 5

    rank_counts = Counter(ranks)
    sorted_counts = sorted(
        rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True
    )
    counts_only = [count for rank, count in sorted_counts]
    sorted_unique_ranks = [rank for rank, count in sorted_counts]

    if is_straight and is_flush:
        return (8, straight_high)
    if counts_only == [4, 1]:
        return (7, sorted_unique_ranks[0], sorted_unique_ranks[1])
    if counts_only == [3, 2]:
        return (6, sorted_unique_ranks[0], sorted_unique_ranks[1])
    if is_flush:
        return (5, ranks)
    if is_straight:
        return (4, straight_high)
    if counts_only == [3, 1, 1]:
        return (
            3,
            sorted_unique_ranks[0],
            sorted_unique_ranks[1],
            sorted_unique_ranks[2],
        )
    if counts_only == [2, 2, 1]:
        return (
            2,
            sorted_unique_ranks[0],
            sorted_unique_ranks[1],
            sorted_unique_ranks[2],
        )
    if counts_only == [2, 1, 1, 1]:
        return (
            1,
            sorted_unique_ranks[0],
            sorted_unique_ranks[1],
            sorted_unique_ranks[2],
            sorted_unique_ranks[3],
        )
    return (0, ranks)
