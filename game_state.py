class GameState:
    def __init__(self, player_manager, district_manager, spymaster):
        print(f"Initialized game state")
        self.player_manager = player_manager
        self.district_manager = district_manager
        self.spymaster = spymaster
        self.num_players = len(self.player_manager.players)
        self.current_player_index = 0  # Start with the first player
        self.turn_number = 1
        self.round = 1 # a round passes when every player has taken their turn once
        print(f"{len(self.player_manager.players)} players, {len(self.district_manager.districts)} districts, {len(self.spymaster.spies)} spies")
        print(f"Turn number {self.turn_number} of round {self.round} - this is {self.player_manager.players[self.current_player_index].name}'s turn.")

    def next_turn(self):
        # Logic to advance to the next player's turn
        print(f"Player index is 'next player index' ({self.current_player_index + 1}) % 'total player count' ({len(self.player_manager.players)})")
        self.current_player_index = (self.current_player_index + 1) % len(self.player_manager.players)
        if self.current_player_index == 0:
            self.turn_number += 1
        self.reset_action_points_for_current_player()
        print(f"Turn advanced to next player, turn number is {self.turn_number}")

    def next_round(self):
        print(f"Called next round on player index {self.current_player_index}, round {self.round}, turn number {self.turn_number}")
        if self.current_player_index == self.num_players:
            self.round += 1
            self.current_player_index = 0
            self.turn_number = 1
        print(f"Round advanced, all players have moved. New round is {self.round}")

    def reset_action_points_for_current_player(self):
        # Resetting the player's AP count right after their turn
        current_player = self.player_manager.players[self.current_player_index]
        current_player.turn_ap = current_player.calculate_action_points()

    def handle_ai_turn(self):
        # Logic for AI's turn if the current player is an AI
        pass