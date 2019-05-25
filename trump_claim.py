from enum import unique, Enum

from deck import BIG_JOKER, SMALL_JOKER, Suit

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

def get_available_claims(player, trump_rank, existing_claim):
       single_claims = []
       pair_claims = []
       joker_claims = []

       claim_dict = {}
       claim_dict[BIG_JOKER] = 0
       claim_dict[SMALL_JOKER] = 0
       for suit in Suit:
          claim_dict[str(suit)] = 0

       for card in player.hand:
           if card.value == trump_rank:
               claim_dict[str(card.suit)] += 1
           
           if str(card) == SMALL_JOKER:
               claim_dict[SMALL_JOKER] += 1
               if claim_dict[SMALL_JOKER] > 1:
                   joker_claims.append(TrumpClaim(TrumpClaimType.JOKER_CLAIM, suit=None))

           if str(card) == BIG_JOKER:
               claim_dict[BIG_JOKER] += 1
               if claim_dict[BIG_JOKER] > 1:
                   joker_claims.append(TrumpClaim(TrumpClaimType.JOKER_CLAIM, suit=None))

       for suit in Suit:
           if claim_dict[str(suit)] > 1:
               pair_claims.append(TrumpClaim(TrumpClaimType.PAIR_RANK_CLAIM, suit))
           elif claim_dict[str(suit)] > 0:
               single_claims.append(TrumpClaim(TrumpClaimType.SINGLE_RANK_CLAIM, suit))

       if not existing_claim:
           return single_claims + pair_claims + joker_claims

       if existing_claim.type == TrumpClaimType.SINGLE_RANK_CLAIM:
           return pair_claims + joker_claims

       if existing_claim.type == TrumpClaimType.PAIR_RANK_CLAIM:
           return joker_claims

       # Last case is a Joker Claim       
       return []
