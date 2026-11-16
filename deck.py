import pygame


class Card:
    def __init__(self, rank, suit, hidden=False):
        self.rank = rank.lower()
        self.suit = suit.lower()[0]
        self.hidden = hidden

    def get(self):
        return f"{self.suit}_{self.rank}"

    def draw(self, screen, position, show=False):
        if self.hidden or not show:
            card_image = pygame.image.load("images/cards/simple_back.svg")
        else:
            card_image = pygame.image.load(f"images/cards/simple_{self.get()}.svg")
        screen.blit(card_image, position)


class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "J",
            "Q",
            "K",
            "A",
        ]
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]

    def shuffle(self):
        import random

        random.shuffle(self.cards)

    def add_card(self, card):
        self.cards.append(card)
        self.shuffle()

    def draw_card(self):
        return self.cards.pop() if self.cards else None
