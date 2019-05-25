from deck import Suit

STARTING_RANK = 2

class Player(object):
    def __init__(self, name, next_player=None, rank=None):
        self.name = name
        self.rank = rank or STARTING_RANK
        self.hand = []
        self.next_player = next_player
        self.points = 0

    def __repr__(self):
        return str(self.name)

    # Sort of weak, but works for now
    def __eq__(self, player2):
        return self.name == player2.name

    def __iter__(self):
        self.curr_iter_player = None
        return self

    def __next__(self):
        if not self.curr_iter_player:
            self.curr_iter_player = self.next_player
            return self.curr_iter_player

        self.curr_iter_player = self.curr_iter_player.next_player
        if self.curr_iter_player == self.next_player:
            raise StopIteration
        return self.curr_iter_player

    def next(self):
        return self.__next__()

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
