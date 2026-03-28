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
    def __init__(self, num_players: int):
        self._game_state = GameState(num_players, self.STARTING_CHIPS, 0, [], 0, 0)
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
            self.players[player_id].update_game_state(self.game_state.get_game_state)
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
                return self.game_state.current_bet == player.my_current_bet  # Can only check if there is no current bet
            case ActionType.CALL:
                return player.my_current_bet < self.game_state.current_bet and \
                       player.chips >= (self.game_state.current_bet - player.my_current_bet)  # Can only call if there is a current bet and player has enough chips
            case ActionType.BET:
                return self.game_state.current_bet == 0 and player.chips > 0
            case ActionType.RAISE:
                return player.chips > (self.game_state.current_bet - player.my_current_bet)  # Can only raise if player has enough chips to at least call
            case ActionType.ALL_IN:
                return True  # All-in is always valid
        return False

    def apply_action(self, player: Player, action: Action):
        if not self.validate_action(player, action):
            raise InvalidActionError(f"Invalid action {action.action_type} by player {player.name}")
        match action.action_type:
            case ActionType.FOLD:
                player.is_playing = False
            case ActionType.CHECK:
                player.check()
            case ActionType.CALL:
                player.call()
            case ActionType.RAISE:
                player.raise_bet()
            case ActionType.ALL_IN:
                player.all_in()

    def betting_round(self):
        for _ in range(len(self.players)):
            current_player = self.get_next_player()

            try:
                print(self.game_state.get_game_state['pot'])
                print(self.game_state.get_game_state['community_cards'])
                print(self.game_state.get_game_state['current_bet'])
                self._game_state.from_dict(current_player.take_action(self.game_state.get_game_state))
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
        small_blind_position = (self.game_state.starting_position) % len(self.players)
        big_blind_position = (self.game_state.starting_position + 1) % len(self.players)

        self.players[small_blind_position].update_game_state(self.game_state.get_game_state)  # Update game state before betting
        self._game_state.from_dict(self.players[small_blind_position].bet())  # Small blind
        self.players[big_blind_position].update_game_state(self.game_state.get_game_state)  # Update game state before betting
        self._game_state.from_dict(self.players[big_blind_position].bet())    # Big blind

    def run_single_game(self):
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
        print(f"The winner is: {winner.name} with hand strength: {winner.hand.evaluate_hand(self.community_cards)[0].name}")

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
    
    @property
    def community_cards(self):
        return self._game_state.community_cards