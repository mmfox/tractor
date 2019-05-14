from enum import unique, Enum

@unique
class Suit(Enum):
    """
    Enum for card suits
    """
    HEARTS = "hearts"
    SPADES = "spades"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"

    def __str__(self):
        return self.value


class Card(object):
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def _value_str(self):
        if self.value < 11:
            return str(self.value)

        if self.value == 11:
            return "Jack"
        if self.value == 12:
            return "Queen"
        if self.value == 13:
            return "King"
        if self.value == 14:
            return "Ace"
        if self.value == 15:
            return "Small Joker"
        if self.value == 16:
            return "Big Joker"

    def __gt__(self, card2):
        return self.value > card2.value

    def __eq__(self, card2):
        return self.value == card2.value and self.suit == card2.suit

    def __str__(self):
        output = self._value_str()

        if self.suit:
            output += " of " + str(self.suit)
      
        return output

    def __repr__(self):
        return str(self)

    @property
    def points(self):
        if self.value == 5:
            return 10
        if self.value == 10 or self.value == 13:
            return 10
        return 0


class Deck(object):
    def __init__(self):
        self.cards = []
        for suit in Suit:
            # Standard Cards
            for value in range(2, 15):
                self.cards.append(Card(suit, value))

        # Small Joker
        self.cards.append(Card(None, 15))

        # Big Joker
        self.cards.append(Card(None, 16))
