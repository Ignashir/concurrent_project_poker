# Enum classes for poker game


from enum import Enum


class ActionType(Enum):
    FOLD = 1
    CHECK = 2
    CALL = 3
    BET = 4
    RAISE = 5
    ALL_IN = 6
    SMALL_BLIND = 7
    BIG_BLIND = 8

class CardSuit(Enum):
    HEARTS = 1
    DIAMONDS = 2
    CLUBS = 3
    SPADES = 4

class CardRank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def __eq__(self, value):
        return super().__eq__(value)
    
    def __lt__(self, other):
        if isinstance(other, CardRank):
            return self.value < other.value
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, CardRank):
            return self.value > other.value
        return NotImplemented
    
    def __hash__(self):
        return super().__hash__()

class HandStrength(Enum):
    ROYAL_FLUSH = 10
    STRAIGHT_FLUSH = 9
    FOUR_OF_A_KIND = 8
    FULL_HOUSE = 7
    FLUSH = 6
    STRAIGHT = 5
    THREE_OF_A_KIND = 4
    TWO_PAIR = 3
    ONE_PAIR = 2
    HIGH_CARD = 1

    def __eq__(self, value):
        return super().__eq__(value)
    
    def __lt__(self, other):
        if isinstance(other, HandStrength):
            return self.value < other.value
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, HandStrength):
            return self.value > other.value
        return NotImplemented

class BettingRound(Enum):
    FLOP = 1
    TURN = 2
    RIVER = 3