# Hand class - represents a player's hand of cards in the poker game and all logic related to evaluating the hand's strength.

from itertools import combinations
from typing import List, Set, Tuple
from collections import Counter

from poker.game_logic.card import Card
from poker.utils.enums import HandStrength, CardRank, CardSuit


class Hand:
    def __init__(self):
        # List of Card objects representing the player's hand
        self.cards: List[Card] = []

    def add_card(self, card_rank: CardRank, card_suit: CardSuit):
        # Add a card to the player's hand
        self.cards.append(Card(card_suit, card_rank))
    
    def add_card(self, card: Card):
        # Add a card to the player's hand
        self.cards.append(card)

    def reset(self):
        # Clear the player's hand for a new game
        self.cards = []

    def evaluate_hand(self, community_cards: List[Card]) -> Tuple[HandStrength, List[int]]:
        """In Texas Holdem version each player can have up to 7 cards, from which only 5 best count.
        Therefore we need to check all combinations of a hand.

        Returns:
            Tuple[HandStrength, List[int]]: best hand strength and the highest cards in the hand for tie-breaking
        """
        best_hand_strength = HandStrength.HIGH_CARD
        best_hand_tiebreaker = []

        # Combine player's hand with community cards
        all_cards = self.cards + community_cards

        # Check all combinations of 5 cards from the player's hand
        for combination in combinations(all_cards, 5):
            hand_strength, tiebreaker = self.evaluate_single_hand(combination)
            if hand_strength.value > best_hand_strength.value:
                best_hand_strength = hand_strength
                best_hand_tiebreaker = tiebreaker
            elif hand_strength.value == best_hand_strength.value:
                # If hand strength is the same, compare tiebreakers
                # TODO needs to be better
                if tiebreaker > best_hand_tiebreaker:
                    best_hand_tiebreaker = tiebreaker

        return best_hand_strength, best_hand_tiebreaker


    def evaluate_single_hand(self, current_hand: List[Card]) -> Tuple[HandStrength, List[int]]:
        """Evalute hand strength

        Returns:
            Tuple[HandStrength, List[int]]: Hand Strength and the highest cards in the hand for tie-breaking
        """
        ranks = sorted([card.rank.value for card in current_hand], reverse=True)
        suits = [card.suit for card in current_hand]

        unique_ranks = set(ranks)
        unique_suits = set(suits)

        rank_counts = Counter(ranks)
        rank_most_common = rank_counts.most_common()
        rank_frequencies = sorted(rank_counts.values(), reverse=True)

        # Check for following hand types in order of strength
        # Check for Royal Flush
        if len(unique_suits) == 1 and set(ranks) == {CardRank.ACE.value, CardRank.KING.value, CardRank.QUEEN.value, CardRank.JACK.value, CardRank.TEN.value}:
            return HandStrength.ROYAL_FLUSH, [CardRank.ACE.value]
        # Check for Straight Flush
        is_straight, straight_high = self.check_straight(unique_ranks)
        if len(unique_suits) == 1 and is_straight:
            return HandStrength.STRAIGHT_FLUSH, [straight_high]  # Return the highest card in the straight flush for tie-breaking
        # Check for Four of a Kind
        if rank_frequencies == [4, 1]:
            return HandStrength.FOUR_OF_A_KIND, [rank_most_common[0][0]] # Return the rank of the four of a kind for tie-breaking
        # Check for Full House
        if rank_frequencies == [3, 2]:
            return HandStrength.FULL_HOUSE, sorted([rank_most_common[0][0], rank_most_common[1][0]], reverse=True) # Return the ranks of the three of a kind and the pair for tie-breaking
        # Check for Flush
        if len(set(suits)) == 1:
            return HandStrength.FLUSH, ranks # Return all card ranks for tie-breaking
        # Check for Straight
        if is_straight:
            return HandStrength.STRAIGHT, [straight_high]  # Return the highest card in the straight for tie-breaking
        # Check for Three of a Kind
        if rank_frequencies == [3, 1, 1]:
            return HandStrength.THREE_OF_A_KIND, [rank_most_common[0][0]] # Return the rank of the three of a kind for tie-breaking
        # Check for Two Pair
        if rank_frequencies == [2, 2, 1]:
            return HandStrength.TWO_PAIR, sorted([rank_most_common[0][0], rank_most_common[1][0]], reverse=True) # Return the ranks of the two pairs for tie-breaking
        # Check for One Pair
        if rank_frequencies == [2, 1, 1, 1]:
            return HandStrength.ONE_PAIR, [rank_most_common[0][0]] # Return the rank of the pair for tie-breaking
        # High Card
        return HandStrength.HIGH_CARD, [ranks[0]] # Return the highest card for tie-breaking

    
    @staticmethod
    def check_straight(ranks: Set[int]) -> Tuple[bool, int]:
        """Check if the hand is a straight (5 consecutive ranks)

        Args:
            ranks (Set[int]): Set of card ranks in the hand
        """
        # If there is not enough unique ranks, it cannot be a straight
        if len(ranks) < 5:
            return False, 0
        sorted_ranks = sorted(ranks)
        # Check for 5 consecutive ranks
        if sorted_ranks[-1] - sorted_ranks[0] == 4:
            return True, sorted_ranks[-1]  # Return the highest card in the straight for tie-breaking
        # Check for Ace-low straight (A-2-3-4-5)
        if {CardRank.ACE.value, CardRank.TWO.value, CardRank.THREE.value, CardRank.FOUR.value, CardRank.FIVE.value} == ranks:
            return True, CardRank.FIVE.value  # Return the highest card in the straight for tie-breaking
        return False, 0