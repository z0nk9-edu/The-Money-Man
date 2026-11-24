import pygame
import deck


class BlackjackPlayer:
    def __init__(self, name, chips=100):
        self.name = name
        self.chips = chips
        self.hand = []

    def receive_card(self, card):
        self.hand.append(card)

    def reset_hand(self):
        self.hand = []

    def get_single_card_value(self, card):
        if card.rank in ["j", "q", "k"]:
            return 10
        elif card.rank == "a":
            return 1  # default to 1
        else:
            return int(card.rank)

    def get_hand_value(self):
        total = 0
        aces = 0
        for card in self.hand:
            value = self.get_single_card_value(card)
            if card.rank == "a":
                aces += 1
                total += 11  # Initially count Ace as 11
            else:
                total += value
        while total > 21 and aces:
            total -= 10  # Convert an Ace from 11 to 1
            aces -= 1
        return total

    def draw(self, surface, position, hide_first_card=False):
        font = pygame.font.Font(None, 36)
        if hide_first_card:
            text = font.render(
                f"{self.name}: {self.chips} chips (Total Value: ?)",
                True,
                (255, 255, 255),
            )
            surface.blit(text, position)
        else:
            text = font.render(
                f"{self.name}: {self.chips} chips (Total Value: {self.get_hand_value()})",
                True,
                (255, 255, 255),
            )
            surface.blit(text, position)
        for i, card in enumerate(self.hand):
            card_x = position[0] + i * 50
            card_y = position[1] + 40
            card.draw(surface, (card_x, card_y))

    # AI Logic

    def calculate_bust_probability(self):
        current_value = self.get_hand_value()
        if current_value >= 21:
            return 1.0
        bust_count = 0
        for card in self.deck.cards:
            if self.get_hand_value() + self.get_single_card_value(card) > 21:
                bust_count += 1
        return bust_count / len(self.deck.cards)

    def get_ai_decision(self, dealer_up_card):
        current_value = self.get_hand_value()
        bust_probability = self.calculate_bust_probability()

        # Automatic Decisions
        if current_value < 12:  # Guaranteed to not bust
            return "hit"
        elif current_value >= 17:
            return "stand"

        if dealer_up_card.rank == "a":
            dealer_value = 11
        else:
            dealer_value = dealer_up_card.get_single_card_value(dealer_up_card)

        # Decision based on dealer's up card
        if dealer_value >= 7:
            risk_tolerance = 0.6
        else:
            risk_tolerance = 0.4

        if bust_probability < risk_tolerance:
            return "hit"
        else:
            return "stand"


class BlackjackGame:
    def __init__(self, human, ai, dealer):
        self.human = human
        self.ai = ai
        self.dealer = dealer
        self.state = "human_turn"  # Possible states: "human_turn", "ai_turn", "dealer_turn", "game_over"
        self.message = "Press [H] to Hit or [S] to Stand"
        self.current_bet = 100
        self.deck = deck.Deck()

    def deal(self):
        for _ in range(2):
            self.human.receive_card(self.deck.draw_card())
            self.ai.receive_card(self.deck.draw_card())
            self.dealer.receive_card(self.deck.draw_card())
        self.dealer.hand[0].hidden = True

    def reset_game(self):
        self.state = "human_turn"
        self.message = "Press [H] to Hit or [S] to Stand"
        for player in [self.human, self.ai, self.dealer]:
            player.reset_hand()
        self.deal()

    def manage_events(self, event):
        print("ye")
        if self.state == "human_turn" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:  # Hit
                self.human.receive_card(self.deck.draw_card())
                if self.human.get_hand_value() > 21:
                    self.state = "ai_turn"
            elif event.key == pygame.K_s:  # Stand
                self.state = "ai_turn"
        elif self.state == "game_over" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Reset
                self.reset_game()

    def update(self):
        if self.state == "ai_turn":
            dealer_up_card = self.dealer.hand[1]
            while self.ai.get_hand_value() < 21:
                decision = self.ai.get_ai_decision(dealer_up_card)
                if decision == "hit":
                    self.ai.receive_card(self.deck.draw_card())
                else:
                    break
            self.state = "dealer_turn"
        elif self.state == "dealer_turn":
            self.dealer.hand[0].hidden = False
            while self.dealer.get_hand_value() < 17:
                self.dealer.receive_card(self.deck.draw_card())
            self.end_round()

    def end_round(self):
        dealer_value = self.dealer.get_hand_value()
        human_value = self.human.get_hand_value()
        ai_value = self.ai.get_hand_value()
        # Human Outcomes
        if human_value > 21:
            self.human.chips -= self.current_bet
            self.message = "You Busted!"
        elif dealer_value > 21 or human_value > dealer_value:
            self.human.chips += self.current_bet
            self.message = "You won!"
        elif human_value < dealer_value:
            self.human.chips -= self.current_bet
            self.message = "You lost!"
        else:
            self.message = "It's a tie!"

        # AI Outcomes
        if ai_value <= 21 and (dealer_value > 21 or ai_value > dealer_value):
            self.ai.chips += self.current_bet
            self.message += " | AI won!"
        elif ai_value > 21 or (dealer_value <= 21 and ai_value < dealer_value):
            self.ai.chips -= self.current_bet
            self.message += " | AI lost!"
        else:
            self.message += " | AI tied!"

        self.message += " | Press [SPACE] to replay game"

        self.state = "game_over"

    def draw(self, screen):
        hide_dealer_card = self.state != "game_over"
        self.dealer.draw(screen, (400, 50), hide_first_card=hide_dealer_card)
        self.human.draw(screen, (50, 400))
        self.ai.draw(screen, (400, 400))

        font = pygame.font.Font(None, 36)
        message_text = font.render(self.message, True, (255, 255, 255))
        screen.blit(message_text, (50, 700))
