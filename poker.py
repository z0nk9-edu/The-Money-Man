import pygame


class PokerPlayer:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = []

    def receive_card(self, card):
        self.hand.append(card)

    def reset_hand(self):
        self.hand = []

    def draw(self, screen, position):
        # Draw the player's hand and chips on the screen
        font = pygame.font.Font(None, 36)
        text = font.render(f"{self.name}: {self.chips} chips", True, (255, 255, 255))
        screen.blit(text, position)
        for i, card in enumerate(self.hand):
            card_image = pygame.image.load(f"images/cards/simple_{card.get()}.svg")
            screen.blit(card_image, (position[0] + i * 50, position[1] + 40))


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

    def draw(self, screen, player):
        player.draw(screen, (50, 50))
        font = pygame.font.Font(None, 36)
        pot_text = font.render(f"Pot: {self.pot} chips", True, (255, 255, 255))
        screen.blit(pot_text, (50, 100))
