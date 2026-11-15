import pygame

class BlackJackPlayer:
    def __init__(self, name, chips, is_AI=False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.is_AI = is_AI

    def receive_card(self, card):
        self.hand.append(card)
    
    def reset_hand(self):
        self.hand = []

    def get_single_card_value(self, card):
        if card.rank in ["J", "Q", "K"]:
            return 10
        elif card.rank == "A":
            return 1  # default to 1
        else:
            return int(card.rank)

    def get_hand_value(self):
        total = 0
        aces = 0
        for card in self.hand:
            value = self.get_single_card_value(card)
            if card.rank == "A":
                aces += 1
                total += 11  # Initially count Ace as 11
            else:
                total += value
        while total > 21 and aces:
            total -= 10  # Convert an Ace from 11 to 1
            aces -= 1
        return total
    
    def draw(self, surface, position, hide_first_card = False):
        font = pygame.font.Font(None, 36)
        if hide_first_card:
            text = font.render(f"{self.name}: {self.chips} chips (Total Value: ?)", True, (255, 255, 255))
            surface.blit(text, position)
        else:
            text = font.render(f"{self.name}: {self.chips} chips (Total Value: {self.get_hand_value()})", True, (255, 255, 255))
            surface.blit(text, position)
        for i, card in enumerate(self.hand):
            card_x = position[0] + i * 50
            card_y = position[1] + 40
            if hide_first_card and i == 0:
                pygame.draw.rect(surface, (0, 0, 0), (card_x, card_y, 40, 60))  # Draw a black rectangle for the hidden card
            else:
                card_image = pygame.image.load(f"images/cards/simple_{card.get()}.png")
                surface.blit(card_image, (card_x, card_y))
        
    # AI Logic

    def calculate_bust_probability(self, deck):
        current_value = self.get_hand_value()
        if current_value >= 21:
            return 1.0
        bust_count = 0
        for card in deck.cards:
            if self.get_hand_value() + self.get_single_card_value(card) > 21:
                bust_count += 1
        return bust_count / len(deck.cards)

    def get_ai_decision(self, deck, dealer_up_card):
        current_value = self.get_hand_value()
        bust_probability = self.calculate_bust_probability(deck)

        # Automatic Decisions
        if current_value < 12: # Guaranteed to not bust
            return "hit"
        elif current_value >= 17:
            return "stand"

        dealer_value = dealer_up_card.get_single_card_value(dealer_up_card)
        if dealer_up_card.rank == "A":
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
            

        
        

        

        
