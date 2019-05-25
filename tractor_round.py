import math
import random

from deck import Suit
from find_friend import FriendRequirement
from play_comparitor import Play, PlayType, PlayComparitor
from player import Player
from rank import get_rank_up
from tractor_deck import TractorDeck
from trump_claim import TrumpClaim, TrumpClaimType

KITTY_MIN = 5
CARDS_PER_DECK = 54

SINGLE_RANK_CLAIM = 1
PAIR_RANK_CLAIM = 2
JOKER_CLAIM = 3

BIG_JOKER_VALUE = 18
SMALL_JOKER_VALUE = 17

class TractorRound(object):
    def __init__(self, num_players, num_decks, active_player, lead_player):
        self.active_player = active_player

        self.lead_player = lead_player
        self.declarer = lead_player
        self.num_players = num_players
        self.num_decks = num_decks
        self.trump_rank = lead_player.rank
        self.trump_suit = None

        self.deck = TractorDeck(num_decks=self.num_decks, kitty_size=self._get_kitty_size())

        self.play_comparitor = None
        self.friend_reqs = []
        self.attacker_set = set()

    def _get_kitty_size(self):
        kitty_size = (self.num_decks * CARDS_PER_DECK) % self.num_players
        while kitty_size < KITTY_MIN:
           kitty_size += self.num_players

        return kitty_size

    def _get_attacking_team_size(self):
        # Special case, ignore standard formula
        if self.num_players == 4:
            return 2

        return math.floor((self.num_players / 2) - 0.1)
 

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
        first_player = self.lead_player
        curr_player = self.lead_player

        trump_claim = None

        while(len(self.deck.undrawn_cards) > 0):
            if curr_player == self.active_player:
                raw_input("Press enter to draw.")

            drawn_card = self.deck.draw()
            curr_player.draw_card(drawn_card)

            if curr_player == self.active_player:
                print("Drew card: " + str(drawn_card))
                print("Current hand: " + str(curr_player.pretty_hand_repr(self.trump_rank)))

            # Give an opportunity to claim
            available_claims = self._player_available_claims(curr_player, trump_claim)
            if len(available_claims) > 0:
                claim = available_claims[0]

                # Let active player not default to first claim
                if curr_player == self.active_player:
                    claim_suit = raw_input("Which suit would you like to claim? Avaliable are: " + str(available_claims) + " or press enter to not claim.\n")

                    claim = next((claim for claim in available_claims if str(claim.suit) == claim_suit), None)
                    if not claim:
                        print("Passed on claim")
                        curr_player = curr_player.next_player
                        continue
               
                if first_game:
                    first_player = curr_player
 
                print("Trump suit claimed by: " + str(curr_player))
                print("Claim type: " + str(claim.type))
                print(claim)
                trump_claim = claim
                self.trump_suit = claim.suit

            # Next player's turn to draw
            curr_player = curr_player.next_player

        self.lead_player = first_player
        self.declarer = first_player
        print("First to act: " + str(self.lead_player))
        print("Final trump suit is: " + str(self.trump_suit))

        self.play_comparitor = PlayComparitor(self.trump_suit, self.trump_rank)

    def handle_kitty(self):
        self.lead_player.hand += self.deck.kitty

        kitty_cards = []
        if self.lead_player == self.active_player:
            print("\n\nYou get the kitty! Please pick " + str(self.deck.kitty_size) + " cards to go back in the kitty.")
            print("Hand with kitty: " + str(self.lead_player.pretty_hand_repr(self.trump_rank)))
            kitty_cards = []
            while len(kitty_cards) != self.deck.kitty_size:
                card_string = raw_input("Pick a card to go back into the kitty.\n")
                kitty_card = None
                for index, card in enumerate(self.lead_player.hand):
                    if card_string == str(card):
                        self.lead_player.hand.pop(index)
                        kitty_card = card
                        break 

                if kitty_card:
                    kitty_cards.append(kitty_card)
                else: 
                    print("Please match the card name exactly as printed above!")

            print("Hand after kitty removed: " + str(self.lead_player.pretty_hand_repr(self.trump_rank)))

        else:
            kitty_cards = self.lead_player.hand[0:self.deck.kitty_size]
            self.lead_player.hand = self.lead_player.hand[self.deck.kitty_size:]

        # Actually set kitty
        self.deck.kitty = kitty_cards

    def _sort_cards(self, cards):
        # Sort cards in descending order
        def func(card):
            return card.comparison_value(self.trump_rank, self.trump_suit)
        return sorted(cards, key = func, reverse=True)

    def make_play(self, player, led_play=None):
        if player == self.active_player:
            valid_play = False
            while not valid_play:
                if led_play:
                    print("\n\nThe lead for this trick was " + str(led_play) + ".  Please follow this lead.")
 
                played_cards_str = raw_input("\n\nPick what to play from your hand (e.g. 2 of clubs, 2 of clubs): \n" + str(player.pretty_hand_repr(self.trump_rank)) + "\n")
                print("\n")

                parsed_played_cards_str = played_cards_str.split(", ") 
                played_cards = []
                indices_to_remove = []

                for played_card_str in parsed_played_cards_str:
                    for index, card in enumerate(player.hand):
                        if played_card_str == str(card) and index not in indices_to_remove:
                            played_cards.append(card)
                            indices_to_remove.append(index)
                            break 

                # Verify we parsed everything correctly
                if len(parsed_played_cards_str) != len(played_cards):
                    print("The play was incorrectly formatted.  Please copy the exact strings printed above to play.")
                    continue

                # Verify is valid play
                # TODO - add verification that the player didn't have to play something else
                played_cards = self._sort_cards(played_cards)
                if not self.play_comparitor.is_valid_lead(played_cards) or (led_play != None and len(led_play.cards) != len(played_cards)):
                    print("The provided play is not valid.  Please play a single card, a pair, top card, or a tractor.  Follow the led play if you are not leading.")
                    continue
                valid_play = True

                # Remove cards from hand
                indices_to_remove.sort(reverse=True)
                for index in indices_to_remove:
                    player.hand.pop(index)
        else:
            if led_play:
                led_type = self.play_comparitor.get_play_type(led_play.cards)
                led_trump_or_suit = led_play.cards[0].trump_or_suit(self.trump_rank, self.trump_suit)
                allowed_cards = [card for card in player.hand if card.trump_or_suit(self.trump_rank, self.trump_suit) == led_trump_or_suit]
                if len(allowed_cards) < len(led_play.cards):
                    player_hand_unallowed_cards = [card for card in player.hand if card not in allowed_cards]
                    allowed_cards += player_hand_unallowed_cards[0:len(led_play.cards)-len(allowed_cards)]

                played_cards = allowed_cards[0:len(led_play.cards)]

                if led_type == PlayType.SINGLE:
                    played_cards = [allowed_cards[0]]
                elif led_type == PlayType.TRACTOR:
                    following_tractors = self.play_comparitor.find_tractors(allowed_cards, led_trump_or_suit, len(led_play.cards))

                    if len(following_tractors) > 0:
                        played_cards = following_tractors[0]
                    else:
                        played_cards = []
                        following_pairs = self.play_comparitor.find_pairs(allowed_cards, led_trump_or_suit)
                        while len(played_cards) < len(led_play.cards) and len(following_pairs) > len(played_cards) / 2:
                            played_cards += following_pairs[len(played_cards) / 2]

                        if len(played_cards) < len(led_play.cards):
                           allowed_unplayed_cards = [card for card in allowed_cards if card not in played_cards]
                           played_cards += allowed_unplayed_cards[0:len(led_play.cards)-len(played_cards)]                            

                elif led_type == PlayType.PAIR:
                    following_pairs = self.play_comparitor.find_pairs(allowed_cards, led_trump_or_suit)
                    if len(following_pairs) > 0:
                        played_cards = following_pairs[0]
                # TODO - implement top card
                elif led_type == PlayType.TOP_CARD:
                    pass
 
                played_cards = self._sort_cards(played_cards)

                indices_to_remove = []
                for played_card in played_cards:
                    for index, card in enumerate(player.hand):
                        if played_card == card and index not in indices_to_remove:
                            indices_to_remove.append(index)
                            break
                   
                indices_to_remove.sort(reverse=True)
                for index in indices_to_remove:
                    player.hand.pop(index)
            else:
                played_cards = [player.hand[0]]
                player.hand.pop(0)


        print(str(player) + " is playing " + str(played_cards))

        # Check if they join the defending team
        for friend_req in self.friend_reqs:
            if friend_req.is_friend(played_cards):
                self.attacker_set.add(player)
                print(str(player) + " has joined the attacking team!  The team is now: " + str(self.attacker_set))

        return Play(player, played_cards)

    def set_friend_reqs(self):
        # The lead player is always in the defender set
        self.attacker_set.add(self.lead_player)

        attacking_team_size = self._get_attacking_team_size()

        if self.lead_player == self.active_player:
            print("\nPlease pick which plays will determine your teammates.  You will have " + str(attacking_team_size - 1) + " additional teammates")
            while len(self.friend_reqs) < attacking_team_size - 1:
                friend_req_str = raw_input("Please input a number of play and a card for the first find friend requirement (e.g. '2, Ace of clubs' would denote the second played Ace of clubs)\n")
                
                parsed_friend_req_str = friend_req_str.split(", ")
                if len(parsed_friend_req_str) != 2 or parsed_friend_req_str[1] not in [str(card) for card in self.deck.cards]:
                    print("Could not parse your input.  Please try again.")
                    continue
                self.friend_reqs.append(FriendRequirement(int(parsed_friend_req_str[0]), parsed_friend_req_str[1]))
        else:
            while len(self.friend_reqs) < attacking_team_size - 1:
                number_play = random.randint(1, 2)
                card = self.deck.cards[random.randint(0, len(self.deck.cards)-1)]
                self.friend_reqs.append(FriendRequirement(number_play, str(card)))

        print("\n\nFind a friend requirements are as follows:")
        print(self.friend_reqs)

    def play_trick(self):
        plays = []
        player_iterator = iter(self.lead_player)
        for player in player_iterator:
            lead_play = plays[0] if plays else None
            plays.append(self.make_play(player, lead_play))

        winning_play = self.play_comparitor.compare_plays(plays)
        print(str(winning_play.player) + " won the round!\n")

        # Calculate points
        points = 0
        for play in plays:
           for card in play.cards:
              points += card.points

        self.lead_player = winning_play.player
        self.lead_player.points += points
            
    def _zero_out_player_points(self):
        player_iterator = iter(self.lead_player)
        for player in player_iterator:
            player.points = 0

    def play(self, first_game=False):
        self.deck.prepare()
        self._zero_out_player_points()

        # Draw cards
        self.draw(first_game)

        # Handle Kitty
        self.handle_kitty()

        # Set find freinds requirements
        self.set_friend_reqs()

        # Let's play tractor
        while len(self.lead_player.hand) > 0:
            self.play_trick()
       
        # Figure out kitty points
        kitty_points = 0
        for card in self.deck.kitty:
            kitty_points += card.points

        if self.lead_player not in self.attacker_set:
            kitty_points *= 2
            print("Attacking team won the kitty!  Double trouble!")

        self.lead_player.points += kitty_points

        # Print results of the round
        print(str(self.lead_player) + " won the kitty, earning an extra " + str(kitty_points) + " for a total of " + str(self.lead_player.points) + " points.\n")
        curr_player = self.lead_player.next_player

        attacking_points = 0
        defending_points = 0

        defender_set = set()
        player_iterator = iter(self.lead_player)
        for player in player_iterator:
            print(str(player) + " earned " + str(player.points) + " points.\n")
            if player in self.attacker_set:
                attacking_points += player.points
            else:
                defender_set.add(player)
                defending_points += player.points

        print("Final attacking team was: " + str(self.attacker_set))
        print("Final defending team was: " + str(defender_set))
        print("Attacking team earned " + str(attacking_points) + " points!")
        print("Defending team earned " + str(defending_points) + " points!")

        attacking_rank_up, defending_rank_up = get_rank_up(defending_points)
        for player in self.attacker_set:
            player.rank += attacking_rank_up
            print(str(player) + " now has a rank of " + str(player.rank))
        for player in defender_set:
            player.rank += defending_rank_up
            print(str(player) + " now has a rank of " + str(player.rank))

        next_round_leader_set = self.attacker_set if attacking_rank_up > 0 else defender_set
        next_round_leader = self.declarer.next_player 
        while next_round_leader not in next_round_leader_set:
            next_round_leader = next_round_leader.next_player
       
        return next_round_leader 
