from typing import Dict, List, Self

from poker.player.player import Player
from poker.utils.enums import ActionType
from poker.game_logic.action import Action

class ConsolePlayer(Player):
    def take_action(self, game_state: Dict) -> Action:
        if not self._is_playing:
            return Action(ActionType.FOLD)  # If player is not playing, they have effectively folded

        while True:
            try:
                action_input = ActionType(int(input(f"{self.name}, choose your action (1: fold, 2: check, 3: call, 4: bet, 5: raise, 6: all-in): ")))

                if action_input == ActionType.RAISE:
                    amount = int(input("Raise amount: "))
                    return Action(action_input, amount)

                return Action(action_input)

            except ValueError:
                print("Invalid input")
    
    @staticmethod
    def create_players(num_players: int, starting_chips: int) -> List[Self]:
        if num_players < 2 or num_players > 10:
            raise ValueError("Number of players must be between 2 and 10.")

        return [ConsolePlayer(f"Player {i + 1}", starting_chips, {}) for i in range(num_players)]