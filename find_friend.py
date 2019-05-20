class FriendRequirement(object):
    def __init__(self, plays_until_friend, card_str):
        self.card_str = card_str
        self.plays_until_friend = plays_until_friend
        self.open = True

    def __str__(self):
        ordinal = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
        return ordinal(self.plays_until_friend) + " " + self.card_str

    def __repr__(self):
        return str(self)

    def is_friend(self, played_cards):
        if self.open:
            for card in played_cards:
                if str(card) == self.card_str and self.plays_until_friend == 1:
                    self.open = False
                    return True
                elif str(card) == self.card_str:
                    self.plays_until_friend -= 1
        return False
