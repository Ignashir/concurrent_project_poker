from typing import Dict, List, Self

from poker.player.player import Player
from poker.utils.enums import ActionType
from poker.game_logic.action import Action

from poker.network.utils import recive_msg, send_msg

YOUR_TURN_MSG = "Your turn"
AMOUNT_MSG = "AMOUNT?"
class NetworkPlayer(Player):
    @property
    def conn(self):
        return getattr(self, "_conn", None)
    
    @conn.setter
    def conn(self, conn):
        self._conn = conn

 
    def take_action(self, game_state: Dict) -> Action:
        try:
            send_msg(YOUR_TURN_MSG, self.conn)

            msg = recive_msg(self.conn)

            if msg == "QUIT":
                raise ConnectionAbortedError()

            action_type = ActionType(int(msg))

            if action_type == ActionType.RAISE:
                send_msg(AMOUNT_MSG, self.conn)

                amount_msg = recive_msg(self.conn)

                if amount_msg == "QUIT":
                    raise ConnectionAbortedError()

                amount = int(amount_msg)
                return Action(action_type, amount)

            return Action(action_type)

        except (ConnectionAbortedError, Exception):
            self.conn = None
            self.is_playing = False
            return Action(ActionType.FOLD)

    @staticmethod
    def create_players(num_players: int, starting_chips: int) -> List[Self]:
        if num_players < 2 or num_players > 10:
            raise ValueError("Number of players must be between 2 and 10.")


        return [NetworkPlayer(f"Player {i + 1}", starting_chips, {}) for i in range(num_players)]