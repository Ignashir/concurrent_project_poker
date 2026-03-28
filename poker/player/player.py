# Player class - represents a player in the poker game

from typing import List, Self, Dict

from poker.game_logic.hand import Hand
from poker.game_logic.card import Card
from poker.utils.enums import ActionType

class Player:
    def __init__(self, name: str, chips: int, game_state: Dict):
        # Name of the player
        self._name: str = name
        # Amount of chips a player has
        self._chips: int = chips
        # The player's current hand of cards
        self.hand: Hand = Hand()
        # Indicates whether the player is still in the current hand (has not folded)
        self._is_playing: bool = True
        # Flag for action taken in the current betting round
        self._action_taken: bool = False
        # Game reference for accessing game state (e.g., current bet, pot)
        self._game = game_state
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

    def take_action(self, game_state: Dict) -> Dict:
        # Placeholder for player action logic (e.g., fold, call, raise)
        self.update_game_state(game_state)

        if not self._is_playing:
            print(f"{self.name} has folded and cannot take an action.")
            return self._game

        self._action_taken = False
        while not self._action_taken:
            try:
                action_input = ActionType(int(input(f"{self.name}, choose your action (1: fold, 2: check, 3: call, 4: bet, 5: raise, 6: all-in): ")))
                match action_input:
                    case ActionType.FOLD:
                        self.fold()
                    case ActionType.CHECK:
                        self.check()
                    case ActionType.CALL:
                        self.call()
                    # TODO Bet is technically only for 2 first players in a game during pre-flop
                    # case ActionType.BET:
                    #     self.bet()
                    case ActionType.RAISE:
                        self.raise_bet()
                    case ActionType.ALL_IN:
                        self.all_in()
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        print(f"{self.name} has finished their action. {self._is_playing}")
        return self._game

    def fold(self):
        print(f"{self.name} has folded.")
        self._is_playing = False
        self._action_taken = True

    def check(self):
        if self._game['current_bet'] > self.my_current_bet:
            print("You cannot check. You must call, raise, or fold.")
        else:
            self._action_taken = True

    def call(self):
        difference = self._game['current_bet'] - self.my_current_bet
        if difference > self._chips:
            print("You don't have enough chips to call. You can go all-in or fold.")
        else:
            self._chips -= difference
            self.my_current_bet += difference
            self._game['pot'] += difference
            self._action_taken = True

    def bet(self) -> Dict:
        bet_amount = int(input("Enter the amount you want to bet: "))
        if bet_amount > self._chips:
            print("You don't have enough chips to bet that amount.")
        else:
            self._chips -= bet_amount
            self.my_current_bet += bet_amount
            self._game['pot'] += bet_amount
            if self.my_current_bet > self._game['current_bet']:
                self._game['current_bet'] = self.my_current_bet
        return self._game

    def raise_bet(self):
        increase_bet = int(input("Enter the amount you want to raise by: "))
        if increase_bet > self._chips:
            print("You don't have enough chips to raise by that amount.")
        else:
            self._chips -= increase_bet
            self.my_current_bet += increase_bet
            self._game['pot'] += increase_bet
            if self.my_current_bet > self._game['current_bet']:
                self._game['current_bet'] = self.my_current_bet
            self._action_taken = True

    def all_in(self):
        try:
            if self._chips > 0:
                all_in_amount = self._chips
                self._chips = 0
                self._game['pot'] += all_in_amount
                self.my_current_bet += all_in_amount
                if self.my_current_bet > self._game['current_bet']:
                    self._game['current_bet'] = self.my_current_bet
                self._action_taken = True
                return all_in_amount
            else:
                self.fold()
                raise ValueError("Player has no chips left to go all-in.")
        except ValueError as e:
            print(f"Error: {e}")
            return 0

    def update_game_state(self, new_state: Dict):
        self._game = new_state

    @property
    def name(self):
        return self._name
    
    @property
    def chips(self):
        return self._chips
    
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
