import pytest

from poker.game_logic.hand import Hand
from poker.utils.enums import CardSuit, HandStrength, CardRank


@pytest.fixture
def royal_flush_hand():
    hand = Hand()
    hand.add_card(CardRank.TEN, CardSuit.HEARTS)
    hand.add_card(CardRank.JACK, CardSuit.HEARTS)
    hand.add_card(CardRank.QUEEN, CardSuit.HEARTS)
    hand.add_card(CardRank.KING, CardSuit.HEARTS)
    hand.add_card(CardRank.ACE, CardSuit.HEARTS)
    return hand


@pytest.fixture
def straight_flush_hand():
    hand = Hand()
    hand.add_card(CardRank.SIX, CardSuit.HEARTS)
    hand.add_card(CardRank.SEVEN, CardSuit.HEARTS)
    hand.add_card(CardRank.EIGHT, CardSuit.HEARTS)
    hand.add_card(CardRank.NINE, CardSuit.HEARTS)
    hand.add_card(CardRank.TEN, CardSuit.HEARTS)
    return hand


@pytest.fixture
def four_of_a_kind_hand():
    hand = Hand()
    hand.add_card(CardRank.JACK, CardSuit.HEARTS)
    hand.add_card(CardRank.JACK, CardSuit.DIAMONDS)
    hand.add_card(CardRank.JACK, CardSuit.CLUBS)
    hand.add_card(CardRank.JACK, CardSuit.SPADES)
    hand.add_card(CardRank.TWO, CardSuit.HEARTS)
    return hand


@pytest.fixture
def full_house_hand():
    hand = Hand()
    hand.add_card(CardRank.KING, CardSuit.HEARTS)
    hand.add_card(CardRank.KING, CardSuit.DIAMONDS)
    hand.add_card(CardRank.KING, CardSuit.CLUBS)
    hand.add_card(CardRank.FOUR, CardSuit.SPADES)
    hand.add_card(CardRank.FOUR, CardSuit.HEARTS)
    return hand


@pytest.fixture
def flush_hand():
    hand = Hand()
    hand.add_card(CardRank.KING, CardSuit.CLUBS)
    hand.add_card(CardRank.NINE, CardSuit.CLUBS)
    hand.add_card(CardRank.SEVEN, CardSuit.CLUBS)
    hand.add_card(CardRank.FIVE, CardSuit.CLUBS)
    hand.add_card(CardRank.TWO, CardSuit.CLUBS)
    return hand


@pytest.fixture
def straight_hand():
    hand = Hand()
    hand.add_card(CardRank.SIX, CardSuit.HEARTS)
    hand.add_card(CardRank.SEVEN, CardSuit.SPADES)
    hand.add_card(CardRank.EIGHT, CardSuit.DIAMONDS)
    hand.add_card(CardRank.NINE, CardSuit.CLUBS)
    hand.add_card(CardRank.TEN, CardSuit.HEARTS)
    return hand


@pytest.fixture
def wheel_straight_hand():
    hand = Hand()
    hand.add_card(CardRank.ACE, CardSuit.HEARTS)
    hand.add_card(CardRank.TWO, CardSuit.SPADES)
    hand.add_card(CardRank.THREE, CardSuit.DIAMONDS)
    hand.add_card(CardRank.FOUR, CardSuit.CLUBS)
    hand.add_card(CardRank.FIVE, CardSuit.HEARTS)
    return hand


@pytest.fixture
def three_of_a_kind_hand():
    hand = Hand()
    hand.add_card(CardRank.SEVEN, CardSuit.HEARTS)
    hand.add_card(CardRank.SEVEN, CardSuit.DIAMONDS)
    hand.add_card(CardRank.SEVEN, CardSuit.SPADES)
    hand.add_card(CardRank.KING, CardSuit.CLUBS)
    hand.add_card(CardRank.TWO, CardSuit.HEARTS)
    return hand


@pytest.fixture
def two_pair_hand():
    hand = Hand()
    hand.add_card(CardRank.ACE, CardSuit.HEARTS)
    hand.add_card(CardRank.ACE, CardSuit.SPADES)
    hand.add_card(CardRank.KING, CardSuit.CLUBS)
    hand.add_card(CardRank.KING, CardSuit.DIAMONDS)
    hand.add_card(CardRank.TWO, CardSuit.HEARTS)
    return hand


@pytest.fixture
def one_pair_hand():
    hand = Hand()
    hand.add_card(CardRank.ACE, CardSuit.HEARTS)
    hand.add_card(CardRank.ACE, CardSuit.SPADES)
    hand.add_card(CardRank.KING, CardSuit.CLUBS)
    hand.add_card(CardRank.NINE, CardSuit.DIAMONDS)
    hand.add_card(CardRank.FOUR, CardSuit.HEARTS)
    return hand


@pytest.fixture
def high_card_hand():
    hand = Hand()
    hand.add_card(CardRank.KING, CardSuit.HEARTS)
    hand.add_card(CardRank.NINE, CardSuit.SPADES)
    hand.add_card(CardRank.SEVEN, CardSuit.DIAMONDS)
    hand.add_card(CardRank.FIVE, CardSuit.CLUBS)
    hand.add_card(CardRank.TWO, CardSuit.HEARTS)
    return hand

def test_royal_flush(royal_flush_hand):
    assert royal_flush_hand.evaluate_hand() == (HandStrength.ROYAL_FLUSH, [CardRank.ACE.value])

def test_straight_flush(straight_flush_hand):
    assert straight_flush_hand.evaluate_hand() == (HandStrength.STRAIGHT_FLUSH, [CardRank.TEN.value])


def test_four_of_a_kind(four_of_a_kind_hand):
    assert four_of_a_kind_hand.evaluate_hand() == (HandStrength.FOUR_OF_A_KIND, [CardRank.JACK.value])


def test_full_house(full_house_hand):
    assert full_house_hand.evaluate_hand() == (HandStrength.FULL_HOUSE, [CardRank.KING.value, CardRank.FOUR.value])


def test_flush(flush_hand):
    assert flush_hand.evaluate_hand() == (HandStrength.FLUSH, [CardRank.KING.value, CardRank.NINE.value, CardRank.SEVEN.value, CardRank.FIVE.value, CardRank.TWO.value])


def test_straight(straight_hand):
    assert straight_hand.evaluate_hand() == (HandStrength.STRAIGHT, [CardRank.TEN.value])


def test_wheel_straight(wheel_straight_hand):
    assert wheel_straight_hand.evaluate_hand() == (HandStrength.STRAIGHT, [CardRank.FIVE.value])


def test_three_of_a_kind(three_of_a_kind_hand):
    assert three_of_a_kind_hand.evaluate_hand() == (HandStrength.THREE_OF_A_KIND, [CardRank.SEVEN.value])


def test_two_pair(two_pair_hand):
    assert two_pair_hand.evaluate_hand() == (HandStrength.TWO_PAIR, [CardRank.ACE.value, CardRank.KING.value])


def test_one_pair(one_pair_hand):
    assert one_pair_hand.evaluate_hand() == (HandStrength.ONE_PAIR, [CardRank.ACE.value])


def test_high_card(high_card_hand):
    assert high_card_hand.evaluate_hand() == (HandStrength.HIGH_CARD, [CardRank.KING.value])

def test_1_plus_card_evaluation_not_better(royal_flush_hand, straight_flush_hand):
    # Test that adding a card to a royal flush does not change its evaluation
    royal_flush_hand.add_card(CardRank.TWO, CardSuit.HEARTS)
    assert royal_flush_hand.evaluate_hand() == (HandStrength.ROYAL_FLUSH, [CardRank.ACE.value])
    
    # Test that adding a card to a straight flush does not change its evaluation
    straight_flush_hand.add_card(CardRank.THREE, CardSuit.HEARTS)
    assert straight_flush_hand.evaluate_hand() == (HandStrength.STRAIGHT_FLUSH, [CardRank.TEN.value])

def test_2_plus_card_evaluation_not_better(straight_hand, flush_hand):
    # Test that adding two cards to a straight does not improve it to a straight flush
    straight_hand.add_card(CardRank.JACK, CardSuit.HEARTS)
    straight_hand.add_card(CardRank.QUEEN, CardSuit.CLUBS)
    assert straight_hand.evaluate_hand() == (HandStrength.STRAIGHT, [CardRank.QUEEN.value])
    
    # Test that adding two cards to a flush does not improve it to a full house
    flush_hand.add_card(CardRank.KING, CardSuit.DIAMONDS)
    flush_hand.add_card(CardRank.QUEEN, CardSuit.SPADES)
    assert flush_hand.evaluate_hand() == (HandStrength.FLUSH, [CardRank.KING.value, CardRank.NINE.value, CardRank.SEVEN.value, CardRank.FIVE.value, CardRank.TWO.value])