import random
from collections import deque
from deck import Deck

class TractorDeck(object):
    def __init__(self, num_decks, kitty_size):
        self.undrawn_cards = [] 
        self.kitty_size = kitty_size
        self.kitty = []

        self.num_decks = num_decks
        self.cards = []
        for _ in range(num_decks):
             deck = Deck()
             self.cards += deck.cards

    def _shuffle(self):
        random.shuffle(self.cards)
        self.undrawn_cards = deque(self.cards)
        
    def _remove_kitty(self):
        self.kitty = []
        for _ in range(self.kitty_size):
            self.kitty.append(self.undrawn_cards.pop())

    def prepare(self):
        self._shuffle()
        self._remove_kitty()

    def draw(self):
        return self.undrawn_cards.pop()


if __name__ == "__main__":
    tractor_deck = TractorDeck(2, 8)

    cards = tractor_deck.cards
    cards.sort()

    for card in cards:
        print(card)

    tractor_deck.prepare()
    
    print("Kitty below")
    for card in tractor_deck.kitty:
        print(card)

    print("Undrawn cards: " + str(len(tractor_deck.undrawn_cards)))
    drawn_card = tractor_deck.draw()
    print("Undrawn cards: " + str(len(tractor_deck.undrawn_cards)))
    print(drawn_card)
