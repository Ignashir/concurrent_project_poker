# Card class - represents a single playing card with a suit and rank.

from dataclasses import dataclass

from poker.utils.enums import CardSuit, CardRank


@dataclass(frozen=True)
class Card:
    suit: CardSuit  # The suit of the card (e.g., 'Hearts', 'Diamonds', 'Clubs', 'Spades')
    rank: CardRank  # The rank of the card (e.g., '2', '3', ..., '10', 'J', 'Q', 'K', 'A')

    def __str__(self):
        return f"{self.rank.name} {self.suit.name}"
    
    def __repr__(self):
        return f"{self.rank.name} {self.suit.name}"