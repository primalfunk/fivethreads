from player import Player
import random

class PlayerManager:
    def __init__(self, num_players):
        self.num_players = num_players
        self.players = []
        self.create_players()

    def create_players(self):
        for i in range(self.num_players):
            player = Player(i)
            player.name = f"Player {i + 1}"
            self.players.append(player)
            print(f"Created player {player.id} name {player.name}")
