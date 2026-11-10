class Card:
    def __init__(self, rank, suit):
        self.rank = rank.lower()
        self.suit = suit.lower()[0]

    def get(self):
        return f"{self.suit}_{self.rank}"
