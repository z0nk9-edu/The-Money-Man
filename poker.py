import pygame


class PokerPlayer:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0

    def place_bet(self, amount):
        if amount > self.chips:
            raise ValueError("Not enough chips to place this bet.")
        self.chips -= amount
        self.current_bet += amount

    def receive_card(self, card):
        self.hand.append(card)

    def reset_hand(self):
        self.hand = []
        self.current_bet = 0

    def draw(self, screen, position):
        # Draw the player's hand and chips on the screen
        font = pygame.font.Font(None, 36)
        text = font.render(f"{self.name}: {self.chips} chips", True, (255, 255, 255))
        screen.blit(text, position)
        for i, card in enumerate(self.hand):
            card_image = pygame.image.load(f"images/cards/simple_{card.get()}.svg")
            screen.blit(card_image, (position[0] + i * 50, position[1] + 40))
