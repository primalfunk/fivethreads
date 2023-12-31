from district_manager import DistrictManager
from game_state import GameState
from player_manager import PlayerManager
from spymaster import SpyMaster

class GameSetup:
    def __init__(self, num_players, num_districts, screen_size):
        self.num_players = num_players
        
        self.player_manager = PlayerManager(num_players)
        self.players = self.player_manager.players
        
        self.num_districts = num_districts
        self.district_manager = DistrictManager(screen_size, self.players, num_districts)
        
        self.spymaster = SpyMaster(self.players, self.district_manager.districts)
        
        self.game_state = GameState(self.player_manager, self.district_manager, self.spymaster)

    