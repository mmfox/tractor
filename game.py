from deck import Suit
from tractor_deck import TractorDeck
from enum import unique, Enum

KITTY_MIN = 5
CARDS_PER_DECK = 54
STARTING_RANK = 2

SINGLE_RANK_CLAIM = 1
PAIR_RANK_CLAIM = 2
JOKER_CLAIM = 3

BIG_JOKER_VALUE = 16
SMALL_JOKER_VALUE = 15

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

class Player(object):
    def __init__(self, name, rank=None):
        self.name = name
        self.rank = rank or STARTING_RANK
        self.hand = []

    def __repr__(self):
        return str(self.name)

    def rank_up(self, rank_increase):
        self.rank += rank_increase

    def draw_card(self, card):
        self.hand.append(card)
       
    def pretty_hand_repr(self, game_rank):
        pretty_hand = []
        for suit in Suit:
             hand_suit = filter(lambda c: c.suit == suit and c.value != game_rank, self.hand)
             hand_suit.sort()
             pretty_hand += hand_suit
        hand_jokers = filter(lambda c: c.suit == None or c.value == game_rank, self.hand)
        hand_jokers.sort()
        pretty_hand += hand_jokers
        return pretty_hand

class Round(object):
    def __init__(self, ordered_players, num_decks, active_player_name):
        self.active_player_name = active_player_name

        self.num_players = len(ordered_players)
        self.num_decks = num_decks
        self.trump_rank = ordered_players[0].rank
        self.trump_suit = None

        self.ordered_players = ordered_players
        self.deck = TractorDeck(num_decks=self.num_decks, kitty_size=self._get_kitty_size())

    def _get_kitty_size(self):
        kitty_size = (self.num_decks * CARDS_PER_DECK) % self.num_players
        while kitty_size < KITTY_MIN:
           kitty_size += self.num_players

        return kitty_size 

    # Figure out if a player can claim right now
    def _player_available_claims(self, player, existing_claim):
       single_claims = []
       pair_claims = []
       joker_claims = []

       claim_dict = {}
       claim_dict["big_joker"] = 0
       claim_dict["small_joker"] = 0
       for suit in Suit:
          claim_dict[str(suit)] = 0

       for card in player.hand:
           if card.value == self.trump_rank:
               claim_dict[str(card.suit)] += 1
           
           if card.value == SMALL_JOKER_VALUE:
               claim_dict["small_joker"] += 1
               if claim_dict["small_joker"] > 1:
                   joker_claims.append(TrumpClaim(TrumpClaimType.JOKER_CLAIM, suit=None))

           if card.value == BIG_JOKER_VALUE:
               claim_dict["big_joker"] += 1
               if claim_dict["big_joker"] > 1:
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


    # Pick a round winner and next lead
    def find_best_card(self, played_cards):
        pass    

    # Handle drawing all cards, setting trump suit
    def draw(self, first_game):
        first_player_index = 0

        trump_claim = None

        while(len(self.deck.undrawn_cards) > 0):
            for index, player in enumerate(self.ordered_players):
                if player.name == self.active_player_name:
                    raw_input("Press enter to draw.")

                drawn_card = self.deck.draw()
                player.draw_card(drawn_card)

                if player.name == self.active_player_name:
                    print("Drew card: " + str(drawn_card))
                    print("Current hand: " + str(player.pretty_hand_repr(self.trump_rank)))

                # Give an opportunity to claim
                available_claims = self._player_available_claims(player, trump_claim)
                if len(available_claims) > 0:
                    claim = available_claims[0]

                    # Let active player not default to first claim
                    if player.name == self.active_player_name:
                        claim_suit = raw_input("Which suit would you like to claim? Avaliable are: " + str(available_claims) + " or press enter to not claim.\n")

                        claim = next((claim for claim in available_claims if str(claim.suit) == claim_suit), None)
                        if not claim:
                            print("Passed on claim")
                            continue
                   
                    if first_game:
                        first_player_index = index
 
                    print("Trump suit claimed by: " + str(player))
                    print("Claim type: " + str(claim.type))
                    print(claim)
                    trump_claim = claim
                    self.trump_suit = claim.suit

        # Reorder players if needed
        self.ordered_players = self.ordered_players[first_player_index:] + self.ordered_players[0:first_player_index]

        print("Newly ordered players: " + str(self.ordered_players))

    def handle_kitty(self):
        kitty_player = self.ordered_players[0]
        kitty_player.hand += self.deck.kitty

        kitty_cards = []
        if kitty_player.name == self.active_player_name:
            print("\n\nYou get the kitty! Please pick " + str(self.deck.kitty_size) + " cards to go back in the kitty.")
            print("Hand with kitty: " + str(kitty_player.pretty_hand_repr(self.trump_rank)))
            kitty_cards = []
            while len(kitty_cards) != self.deck.kitty_size:
                card_string = raw_input("Pick a card to go back into the kitty.\n")
                kitty_card = None
                for index, card in enumerate(kitty_player.hand):
                    if card_string == str(card):
                        kitty_player.hand.pop(index)
                        kitty_card = card
                        break 

                if kitty_card:
                    kitty_cards.append(kitty_card)
                else: 
                    print("Please match the card name exactly as printed above!")

            print("Hand after kitty removed: " + str(kitty_player.pretty_hand_repr(self.trump_rank)))

        else:
            kitty_cards = kitty_player.hand[0:self.deck.kitty_size]
            kitty_player.hand = kitty_player.hand[self.deck.kitty_size:]

        # Actually set kitty
        self.deck.kitty = kitty_cards
            

    def play(self, first_game=False):
        self.deck.prepare()

        # Draw cards
        self.draw(first_game)

        # Handle Kitty
        self.handle_kitty()

if __name__ == "__main__":
    players = [Player("Matt"), Player("Roger"), Player("Carlo"), Player("Aviv")] 
    tractor_round = Round(players, num_decks=2, active_player_name="Matt")

    tractor_round.play(first_game=True)
