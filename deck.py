class Card:
    def __init__(self, rank, suit):
        self.rank = rank.lower()
        self.suit = suit.lower()[0]

    def get(self):
        return f"{self.suit}_{self.rank}"


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
