# Card deck class - represents a standard deck of 52 playing cards and includes methods for shuffling and dealing cards.

import random

from poker.game_logic.card import Card
from poker.utils.enums import CardSuit, CardRank


class CardDeck:
    def __init__(self):
        # Initialize a standard deck of 52 cards
        self.cards = self._create_deck()

    def _create_deck(self):
        # Create a standard deck of 52 cards (13 ranks x 4 suits)
        return [Card(suit=suit, rank=rank) for suit in CardSuit for rank in CardRank]

    def shuffle(self):
        # Shuffle the deck of cards
        random.shuffle(self.cards)

    def deal_card(self):
        # Deal a single card from the top of the deck
        if self.cards:
            return self.cards.pop(0)  # Remove and return the top card
        else:
            raise ValueError("No more cards in the deck")

    def deal_cards(self, num_cards):
        # Deal a specified number of cards from the top of the deck
        if num_cards <= len(self.cards):
            dealt_cards = self.cards[:num_cards]  # Get the top num_cards
            self.cards = self.cards[num_cards:]  # Remove the dealt cards from the deck
            return dealt_cards
        else:
            raise ValueError("Not enough cards in the deck to deal")

    def reset_deck(self):
        # Reset the deck to a full set of 52 cards and shuffle it
        self.cards = self._create_deck()
        self.shuffle()
    
    def cards_remaining(self):
        # Return the number of cards remaining in the deck
        return len(self.cards)
    
    def is_empty(self):
        # Check if the deck is empty
        return self.cards_remaining() == 0