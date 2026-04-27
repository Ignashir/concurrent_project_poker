from typing import List

from poker.player.player import Player
from poker.game_logic.card_deck import CardDeck
from poker.game.game_state import GameState
from poker.game_logic.action import Action
from poker.utils.enums import HandStrength, BettingRound, ActionType
from poker.utils.errors import InvalidActionError


class Game:
    STARTING_CHIPS = 1000
    SMALL_BLIND = 10
    BIG_BLIND = 20

    def __init__(self, players: List[Player]):
        self._game_state = GameState(players)
        self._card_deck = CardDeck()

    def clean_state(self):
        self._game_state.reset_state()
        self._card_deck.reset_deck()

    def start_game(self):
        self.clean_state()
        for player in self.players:
            player.reset_hand()
        self.card_deck.reset_deck()

    def deal_cards(self):
        for player_id in range(len(self.players)):
            self.players[player_id].is_playing = True
            for _ in range(2):
                self.players[player_id].take_card(self.card_deck.deal_card())

    def active_players(self) -> List[Player]:
        return [p for p in self.players if p.is_playing]

    def get_next_player(self):
        current_position = self.game_state.current_player_index
        avoid_infinite_loop_counter = 0
        while avoid_infinite_loop_counter < len(self.players):
            player = self.players[current_position]
            if player.is_playing and player.chips > 0:
                self._game_state.current_player_index = (current_position + 1) % len(self.players)
                return player
            current_position = (current_position + 1) % len(self.players)
            avoid_infinite_loop_counter += 1   
        return None

    def validate_action(self, player: Player, action: Action) -> bool:
        match action.action_type:
            case ActionType.FOLD:
                return True
            case ActionType.CHECK:
                return self.current_bet == player.my_current_bet
            case ActionType.CALL:
                return (
                    player.my_current_bet < self.current_bet
                    and player.chips >= (self.current_bet - player.my_current_bet)
                )
            case ActionType.RAISE:
                if action.amount is None or action.amount <= 0:
                    return False
                new_total_bet = player.my_current_bet + action.amount
                return (
                    player.chips >= action.amount 
                    and new_total_bet > self.current_bet
                )
            case ActionType.ALL_IN:
                return player.chips > 0
            case ActionType.SMALL_BLIND | ActionType.BIG_BLIND:
                return True if self.blinds_posting else False
        return False

    def apply_raise(self, player: Player, amount: int):
        player.chips -= amount
        player.my_current_bet += amount
        self.pot += amount
        if player.my_current_bet > self.current_bet:
            self.current_bet = player.my_current_bet

    def apply_action(self, player: Player, action: Action):
        if not self.validate_action(player, action):
            raise InvalidActionError(f"Invalid action {action.action_type} by player {player.name}")
        match action.action_type:
            case ActionType.FOLD:
                player.is_playing = False
            case ActionType.CHECK:
                pass
            case ActionType.CALL:
                difference = self.current_bet - player.my_current_bet
                self.apply_raise(player, difference)
            case ActionType.RAISE:
                self.apply_raise(player, action.amount)
            case ActionType.ALL_IN:
                all_in_amount = player.chips
                self.apply_raise(player, all_in_amount)
            case ActionType.SMALL_BLIND:
                amount = min(self.SMALL_BLIND, player.chips)
                self.apply_raise(player, amount)
            case ActionType.BIG_BLIND:
                amount = min(self.BIG_BLIND, player.chips)
                self.apply_raise(player, amount)

    def betting_round(self):
        to_act = {p.name for p in self.active_players() if p.chips > 0}
        
        if len(to_act) <= 1:
            return

        while to_act:
            current_player = self.get_next_player()
            if current_player is None or current_player.name not in to_act:
                if not any(name in to_act for name in [p.name for p in self.active_players()]):
                    break
                continue

            while True:
                try:
                    state = self.game_state.get_game_state
                    print(f"\nPot: {state['pot']} | Community: {state['community_cards']}")
                    print(f"Current Bet: {state['current_bet']}")
                    print(f"{current_player.name} (Chips: {current_player.chips}, My Bet: {current_player.my_current_bet})")
                    old_bet = self.current_bet
                    
                    action = current_player.take_action(state)
                    self.apply_action(current_player, action)
                    
                    print(f"{current_player.name} performed: {action.action_type.name}")

                    if current_player.name in to_act:
                        to_act.remove(current_player.name)

                    if self.current_bet > old_bet:
                        for p in self.active_players():
                            if p != current_player and p.chips > 0:
                                to_act.add(p.name)

                    if not current_player.is_playing:
                        if current_player.name in to_act:
                            to_act.remove(current_player.name)
                            
                    break
                except InvalidActionError as invalid:
                    print(f"Error: {invalid}")
            if len(self.active_players()) <= 1:
                break

    def reveal_community_cards(self, betting_round: BettingRound):
        match betting_round:
            case BettingRound.FLOP:
                self._game_state.community_cards.extend(self.card_deck.deal_cards(3))
            case BettingRound.TURN:
                self._game_state.community_cards.append(self.card_deck.deal_card())
            case BettingRound.RIVER:
                self._game_state.community_cards.append(self.card_deck.deal_card())

    def determine_winner(self):
        active = self.active_players()
        if len(active) == 1:
            return active[0]

        winner = None
        best_hand_strength = HandStrength.HIGH_CARD
        best_hand_tiebreaker = []

        for player in active:
            hand_strength, tiebreaker = player.hand.evaluate_hand(self.community_cards)
            if hand_strength.value > best_hand_strength.value:
                best_hand_strength = hand_strength
                best_hand_tiebreaker = tiebreaker
                winner = player
            elif hand_strength.value == best_hand_strength.value:
                if tiebreaker > best_hand_tiebreaker:
                    best_hand_tiebreaker = tiebreaker
                    winner = player

        return winner

    def perform_initial_bets(self):
        small_blind_position = self.game_state.starting_position % len(self.players)
        big_blind_position = (small_blind_position + 1) % len(self.players)

        small_blind_player = self.players[small_blind_position]
        big_blind_player = self.players[big_blind_position]

        self.blinds_posting = True
        self.apply_action(small_blind_player, Action(ActionType.SMALL_BLIND, self.SMALL_BLIND))
        self.apply_action(big_blind_player, Action(ActionType.BIG_BLIND, self.BIG_BLIND))
        self.blinds_posting = False

        self._game_state.current_player_index = (big_blind_position + 1) % len(self.players)

    def run_single_game(self) -> Player:
        self.start_game()
        self.perform_initial_bets()
        self.deal_cards()
        for betting_round in BettingRound:
            self.betting_round()
            if len(self.active_players()) <= 1:
                break
            self.reveal_community_cards(betting_round)
        
        winner = self.determine_winner()
        if winner:
            print(f"Winner: {winner.name} wins: {self.pot} chips!")
            winner.chips += self.pot
            winner.hands_won += 1
            self.pot = 0
        else:
            print("Error")
        return winner

    @property
    def players(self):
        return self._game_state.players

    @property
    def game_state(self):
        return self._game_state

    @property
    def card_deck(self):
        return self._card_deck

    @property
    def pot(self):
        return self._game_state.pot

    @pot.setter
    def pot(self, amount):
        self._game_state.pot = amount

    @property
    def current_bet(self):
        return self._game_state.current_bet

    @current_bet.setter
    def current_bet(self, amount):
        self._game_state.current_bet = amount

    @property
    def community_cards(self):
        return self._game_state.community_cards

    @property
    def blinds_posting(self):
        return self._game_state.blinds_posting

    @blinds_posting.setter
    def blinds_posting(self, value: bool):
        self._game_state.blinds_posting = value