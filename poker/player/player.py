# Player class - represents a player in the poker game

from typing import List, Self, Dict
from abc import ABC, abstractmethod

from poker.game_logic.hand import Hand
from poker.game_logic.card import Card
from poker.utils.enums import ActionType
from poker.game_logic.action import Action

class Player(ABC):
    def __init__(self, name: str, chips: int, game_state: Dict):
        # Name of the player
        self._name: str = name
        # Amount of chips a player has
        self._chips: int = chips
        # The player's current hand of cards
        self.hand: Hand = Hand()
        # Indicates whether the player is still in the current hand (has not folded)
        self._is_playing: bool = True
        # Player's current bet in the ongoing betting round
        self.my_current_bet: int = 0
        # Additional statistics
        self.hands_played: int = 0
        self.hands_won: int = 0
        self.saldo: int = 0

    def take_card(self, card: Card):
        self.hand.add_card(card)

    def reset_hand(self):
        self.hand.reset()
        self.my_current_bet = 0

    @abstractmethod
    def take_action(self, game_state: Dict) -> Action:
        pass

    @property
    def name(self):
        return self._name
    
    @property
    def chips(self):
        return self._chips
    
    @chips.setter
    def chips(self, amount):
        if amount < 0:
            raise ValueError("Chips cannot be negative.")
        self._chips = amount
    
    @property
    def is_playing(self):
        return self._is_playing
    
    @is_playing.setter
    def is_playing(self, value: bool):
        self._is_playing = value

    @staticmethod
    def create_players(num_players: int, starting_chips: int) -> List[Self]:
        if num_players < 2 or num_players > 10:
            raise ValueError("Number of players must be between 2 and 10.")

        return [Player(f"Player {i + 1}", starting_chips, {}) for i in range(num_players)]
