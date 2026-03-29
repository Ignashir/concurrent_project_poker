from random import randint
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
        self._game_state = GameState(players, self.STARTING_CHIPS, 0, [], 0, 0)
        self._card_deck = CardDeck()

    def clean_state(self):
        """Reset the game state for a new game."""
        self._game_state.reset_state(len(self.players), self.STARTING_CHIPS)
        self._card_deck.reset_deck()

    def start_game(self):
        """Initiate Players + reset the card deck + deal cards - Prepare the clean state

        Args:
            num_players (int): _description_

        Raises:
            ValueError: _description_
        """
        # Reset statistics from previous game
        self.clean_state()
        
        # Reset Players hands
        for player in self.players:
            player.reset_hand()

        # Reset CardDeck
        self.card_deck.reset_deck()

    def deal_cards(self):
        # Deal hole cards to each player
        for player_id in range(len(self.players)):
            self.players[player_id].is_playing = True
            for _ in range(2):  # Deal 2 hole cards to each player
                self.players[player_id].take_card(self.card_deck.deal_card())

    def get_next_player(self):
        # Get the next player who is still in the game
        current_position = self.game_state.current_player_index
        avoid_infinite_loop_counter = 0
        # Search for a next player who is still playing
        while avoid_infinite_loop_counter < len(self.players):
            if self.players[current_position].is_playing:
                self._game_state._current_player_index = (current_position + 1) % len(self.players)
                return self.players[current_position]
            current_position = (current_position + 1) % len(self.players)
            avoid_infinite_loop_counter += 1
        raise ValueError("No players are currently playing.")

    def validate_action(self, player: Player, action: Action) -> bool:
        # Implement validation logic for actions (e.g., cannot check if there is a current bet, cannot call if not enough chips)
        match action.action_type:
            case ActionType.FOLD:
                return True  # Folding is always valid
            case ActionType.CHECK:
                return self.current_bet == player.my_current_bet  # Can only check if there is no current bet
            case ActionType.CALL:
                return player.my_current_bet < self.current_bet and \
                       player.chips >= (self.current_bet - player.my_current_bet)  # Can only call if there is a current bet and player has enough chips
            case ActionType.RAISE:
                return player.chips > (self.current_bet - player.my_current_bet)  # Can only raise if player has enough chips to at least call
            case ActionType.ALL_IN:
                return player.chips > 0  # Can go all-in if player has any chips left
            case ActionType.SMALL_BLIND | ActionType.BIG_BLIND:
                return True if self.blinds_posting else False  # Blinds can only be posted during the initial betting round
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
                pass  # No chips are moved for a check
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
        for _ in range(len(self.players)):
            current_player = self.get_next_player()
            while True:
                try:
                    print(f"Pot: {self.game_state.get_game_state['pot']}")
                    print(f"Community Cards: {self.game_state.get_game_state['community_cards']}")
                    print(f"Current Bet: {self.game_state.get_game_state['current_bet']}")
                    action = current_player.take_action(self.game_state.get_game_state)
                    self.apply_action(current_player, action)
                    print(f"{current_player.name} performed action: {action.action_type.name} with amount: {action.amount if action.amount else 'N/A'}")
                    break  # Exit the loop if action is successfully applied
                except InvalidActionError as invalid:
                    print(f"Error: {invalid}")

    def reveal_community_cards(self, betting_round: BettingRound):
        match betting_round:
            case BettingRound.FLOP:
                self._game_state.community_cards.extend(self.card_deck.deal_cards(3))
            case BettingRound.TURN:
                self._game_state.community_cards.append(self.card_deck.deal_card())
            case BettingRound.RIVER:
                self._game_state.community_cards.append(self.card_deck.deal_card())

    def determine_winner(self):
        winner = None
        best_hand_strength = HandStrength.HIGH_CARD
        best_hand_tiebreaker = None

        for player in self.players:
            if player.is_playing:
                hand_strength, tiebreaker = player.hand.evaluate_hand(self.community_cards)
                if hand_strength.value > best_hand_strength.value:
                    best_hand_strength = hand_strength
                    best_hand_tiebreaker = tiebreaker
                    winner = player
                elif hand_strength.value == best_hand_strength.value:
                    # If hand strength is the same, compare tiebreakers
                    if tiebreaker > best_hand_tiebreaker:
                        best_hand_tiebreaker = tiebreaker
                        winner = player
        return winner

    def perform_initial_bets(self):
        # Perform initial bets (small blind and big blind)
        small_blind_position = self.game_state.starting_position % len(self.players)
        big_blind_position = (small_blind_position + 1) % len(self.players)

        small_blind_player = self.players[small_blind_position]
        big_blind_player = self.players[big_blind_position]
        
        self.blinds_posting = True
        self.apply_action(small_blind_player, Action(ActionType.SMALL_BLIND, self.SMALL_BLIND))
        self.apply_action(big_blind_player, Action(ActionType.BIG_BLIND, self.BIG_BLIND))
        self.blinds_posting = False

        # Set who starts (player after big blind)
        self._game_state.current_player_index = (big_blind_position + 1) % len(self.players)

    def run_single_game(self) -> Player:
        # Reset game state
        self.start_game()
        # Perform first 2 bets
        self.perform_initial_bets()
        # Deal 2 cards to each player
        self.deal_cards()
        for betting_round in BettingRound:
            # Perform betting round
            self.betting_round()
            self.reveal_community_cards(betting_round)
        # Determine winner
        winner = self.determine_winner()
        return winner

    # def run(self):
    #     self.start_game(len(self.players))
    #     while True:
    #         self.run_single_game()

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