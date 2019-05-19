from enum import unique, Enum

from deck import (Suit, Card, TRUMP_SUIT)

@unique
class PlayType(Enum):
    """
    Enum for play types
    """
    SINGLE = "single"
    PAIR = "pair"
    TRACTOR = "tractor"
    TOP_CARD = "top-card"

    # A play that follows a lead may not be a cogent play
    FOLLOW = "follow"

    def __str__(self):
        return self.value

class Play(object):
    def __init__(self, player, cards):
        self.player = player
        self.cards = cards

    def __str__(self):
        return str(self.player) + " played " + str(self.cards)

    def __repr__(self):
        return str(self)


class PlayComparitor(object):
    def __init__(self, trump_suit, trump_rank):
        self.trump_suit = trump_suit
        self.trump_rank = trump_rank

    def compare_plays(self, plays):
        assert(len(plays))
        winning_play = None
    
        for play in plays:
            if not winning_play:
                winning_play = play
            else:
                winning_play = self._get_better_play(winning_play, play)
    
        return winning_play

    def _get_better_play(self, winning_play, new_play):
        if self._is_pair(winning_play.cards) and not self._is_pair(new_play.cards):
            return winning_play
        elif self._is_tractor(winning_play.cards) and not self._is_tractor(new_play.cards):
            return winning_play
        elif self._is_top_card(winning_play.cards):
            pass
        
        # Single card comparison will do at this point
        winning_value = winning_play.cards[0].comparison_value(self.trump_rank, self.trump_suit)
        new_value = new_play.cards[0].comparison_value(self.trump_rank, self.trump_suit)
        winning_suit = winning_play.cards[0].trump_or_suit(self.trump_rank, self.trump_suit)
        new_suit = new_play.cards[0].trump_or_suit(self.trump_rank, self.trump_suit)
    
        if new_suit == TRUMP_SUIT and winning_suit != TRUMP_SUIT:
            return new_play
        
        return new_play if new_value > winning_value and new_suit == winning_suit else winning_play

    def is_valid_lead(self, cards):
        if len(cards) == 1 or self._is_top_card(cards) or self._is_pair(cards) or self._is_tractor(cards):
            return True
        return False

    def get_play_type(self, cards):
        if len(cards) == 1:
            return PlayType.SINGLE
        elif self._is_tractor(cards):
            return PlayType.TRACTOR
        elif self._is_pair(cards):
            return PlayType.PAIR
        elif self._is_top_card(cards):
            return PlayType.TOP_CARD

        return PlayType.FOLLOW

    # Currently need to have a suit since pairs will not be sectioned by suit just yet
    # TODO - support splitting pairs into suits
    def find_tractors(self, cards, trump_or_suit, tractor_length=None):
        tractors = []
        pairs = self.find_pairs(cards, trump_or_suit)

        def func(pair):
            return pair[0].comparison_value(self.trump_rank, self.trump_suit)

        pairs.sort(key = func)

        for index, pair in enumerate(pairs):
            pair_value = pair[0].comparison_value(self.trump_rank, self.trump_suit)
            next_index = index+1
            while next_index < len(pairs) and pairs[next_index][0].comparison_value(self.trump_rank, self.trump_suit) == (pair_value + next_index - index):
                next_index += 1
            if next_index-index > 1 and (not tractor_length or next_index - index == tractor_length):
                tractor = []
                for i in range(index, next_index):
                    tractor += pairs[i]
                tractors.append(tractor)

        return tractors

    def find_pairs(self, cards, trump_or_suit=None):
        pair_dict = {}
        pairs = []
      
        for card in cards:
            if str(card) in pair_dict:
                pairs.append([pair_dict[str(card)], card])
            if not trump_or_suit or card.trump_or_suit(self.trump_rank, self.trump_suit) == trump_or_suit: 
                pair_dict[str(card)] = card

        return pairs
        
    # TODO - implement top card
    def _is_top_card(self, cards):
        return False
    
    def _is_pair(self, cards):
        if len(cards) == 2:
            return cards[0].suit == cards[1].suit and cards[0].value == cards[1].value
        return False
    
    def _is_tractor(self, cards):
        if len(cards) > 2 and len(cards) % 2 == 0:
            prev_pair_card = None
            for pair_num in range(len(cards) / 2):
                pair_start_index = 2*pair_num
                if not self._is_pair(cards[pair_start_index:pair_start_index+2]):
                    return False
                if prev_pair_card and (cards[pair_start_index].comparison_value(self.trump_rank, self.trump_suit) != prev_pair_card.comparison_value(self.trump_rank, self.trump_suit) - 1 or cards[pair_start_index].trump_or_suit(self.trump_rank, self.trump_suit) != prev_pair_card.trump_or_suit(self.trump_rank, self.trump_suit)): 
                    return False
                prev_pair_card = cards[pair_start_index]
            return True
        return False


if __name__ == "__main__":
   cards = [Card(Suit.DIAMONDS, 4), Card(Suit.DIAMONDS, 4), Card(Suit.DIAMONDS, 3), Card(Suit.DIAMONDS, 3), Card(Suit.DIAMONDS, 2), Card(Suit.DIAMONDS, 2), Card(Suit.SPADES, 2), Card(Suit.SPADES, 2)]
   comparitor = PlayComparitor(Suit.DIAMONDS, 2)
   tractors = comparitor.find_tractors(cards, "trump_suit") 

   print(tractors)
