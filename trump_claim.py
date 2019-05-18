from enum import unique, Enum

@unique
class TrumpClaimType(Enum):
    """
    Enum for trump claim types
    """
    SINGLE_RANK_CLAIM = 1
    PAIR_RANK_CLAIM = 2
    JOKER_CLAIM = 3

    def __str__(self):
        return str(self.value)

class TrumpClaim(object):
    def __init__(self, claim_type, suit):
        self.type = claim_type
        self.suit = suit

    def __repr__(self):
        return str(self.suit)
