import pygame

class BlackJackPlayer:
    def __init__(self, name, chips, is_AI=False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.is_AI = is_AI

    
