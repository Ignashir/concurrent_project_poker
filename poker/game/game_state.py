import random
from typing import List

from poker.player.player import Player
from poker.game_logic.card import Card


class GameState:
    def __init__(self, num_players: int, starting_chips: int, pot: int, community_cards: List[Card], current_bet: int, starting_position: int):
        self._players = Player.create_players(num_players, starting_chips)
        self._pot = pot
        self._community_cards = community_cards
        self._current_bet = current_bet
        self._starting_position = starting_position
        self._current_player_index = starting_position

    def from_dict(self, state_dict):
        self._players = state_dict['players']
        self._pot = state_dict['pot']
        self._community_cards = state_dict['community_cards']
        self._current_bet = state_dict['current_bet']
        self._starting_position = state_dict['starting_position']
        self._current_player_index = state_dict['current_player_index']

    def reset_state(self, num_players: int, starting_chips: int):
        self._players = Player.create_players(num_players, starting_chips)
        self._starting_position = random.randint(0, num_players - 1)
        self._pot = 0
        self._community_cards = []
        self._current_bet = 0
        self._current_player_index = self._starting_position

    @property
    def players(self):
        return self._players
    
    @property
    def current_bet(self):
        return self._current_bet

    @current_bet.setter
    def current_bet(self, amount):
        if amount < 0:
            raise ValueError("Current bet cannot be negative.")
        self._current_bet = amount

    @property
    def starting_position(self):
        return self._starting_position
    
    @property
    def community_cards(self):
        return self._community_cards

    @community_cards.setter
    def community_cards(self, cards: List[Card]):
        if not all(isinstance(card, Card) for card in cards):
            raise ValueError("All items in community_cards must be instances of Card.")
        self._community_cards = cards
    
    @property
    def pot(self):
        return self._pot
    
    @pot.setter
    def pot(self, amount):
        if amount < 0:
            raise ValueError("Pot amount cannot be negative.")
        self._pot += amount

    @property
    def current_player_index(self):
        return self._current_player_index

    @current_player_index.setter
    def current_player_index(self, index):
        if index < 0 or index >= len(self._players):
            raise ValueError("Player index out of range.")
        self._current_player_index = index

    @property
    def get_game_state(self):
        return {
            "players": self.players,
            "pot": self.pot,
            "community_cards": self.community_cards,
            "current_bet": self.current_bet,
            "starting_position": self.starting_position,
            "current_player_index": self.current_player_index
        }