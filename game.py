from constants import WINNING_RANK
from player import Player
from tractor_round import TractorRound

class Game(object):
    def __init__(self, num_players, num_decks, active_player):
        self.active_player = active_player
        self.num_players = num_players
        self.num_decks = num_decks

    def play(self):
        first_game = True
        winner = None
        lead_player = self.active_player
        while not winner:
            tractor_round = TractorRound(num_players=self.num_players, num_decks=self.num_decks, active_player=self.active_player, lead_player=lead_player)
            lead_player = tractor_round.play(first_game=first_game)
            first_game=False 
            
            player_iterator = iter(self.active_player)
            for player in player_iterator:
                if player.rank >= WINNING_RANK and (not winner or player.rank > winner.rank):
                    winner = player

        print("\n\nGame complete!  " + str(winner) + " has won!\n")
        

if __name__ == "__main__":
    matt = Player("Matt") 
    roger = Player("Roger", matt)
    carlo = Player("Carlo", roger)
    aviv = Player("Aviv", carlo)
    matt.next_player = aviv 
    game = Game(num_players=4, num_decks=2, active_player=matt)

    game.play()
