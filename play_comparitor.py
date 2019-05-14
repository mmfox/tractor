#
#
#  cards are sorted in descending order
#  Play
#    cards = []
#    Player

from deck import (Suit, Card)

TRUMP_SUIT = "trump_suit"

class Play(object):
    def __init__(self, player, cards):
        self.player = player
        self.cards = cards


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
        winning_suit = self._trump_or_suit(winning_play.cards[0])
        new_suit = self._trump_or_suit(new_play.cards[0])
    
        if new_suit == TRUMP_SUIT and winning_suit != TRUMP_SUIT:
            return new_play
        
        return new_play if new_value > winning_value and new_suit == winning_suit else winning_play

    # TODO - implement top card
    def _is_top_card(self, cards):
        pass
    
    def _is_pair(self, cards):
        if len(cards) == 2:
            return cards[0].suit == cards[1].suit and cards[0].value == cards[1].value
        return False
    
    def _is_tractor(self, cards):
        if len(cards) % 2 == 0:
            prev_pair_card = None
            for pair_num in range(len(cards) / 2):
                pair_start_index = 2*pair_num
                if not self._is_pair(cards[pair_start_index:pair_start_index+2]):
                    return False
                if prev_pair_card and (cards[pair_start_index].comparison_value(self.trump_rank, self.trump_suit) != prev_pair_card.comparison_value(self.trump_rank, self.trump_suit) - 1 or self._trump_or_suit(cards[pair_start_index]) != self._trump_or_suit(prev_pair_card)): 
                    return False
                prev_pair_card = cards[pair_start_index]
            return True
        return False

    def _trump_or_suit(self, card):
        if card.value == self.trump_rank or card.suit == self.trump_suit or card.suit == None:
            return TRUMP_SUIT
    
        return card.suit

if __name__ == "__main__":
   plays = [Play(None, [Card(Suit.DIAMONDS, 4), Card(Suit.DIAMONDS, 4), Card(Suit.DIAMONDS, 3), Card(Suit.DIAMONDS, 3)]), Play(None, [Card(Suit.DIAMONDS, 7), Card(Suit.DIAMONDS, 7), Card(Suit.DIAMONDS, 6), Card(Suit.DIAMONDS, 6)]), Play(None, [Card(Suit.HEARTS, 11), Card(Suit.HEARTS, 11), Card(Suit.HEARTS, 10), Card(Suit.HEARTS, 10)])]
   comparitor = PlayComparitor(None, 2)
   better_play = comparitor.compare_plays(plays)
   print(better_play.cards)
