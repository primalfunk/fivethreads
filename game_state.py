class GameState:
    def __init__(self, player_manager, district_manager, spymaster):
        self.player_manager = player_manager
        self.district_manager = district_manager
        self.spymaster = spymaster

        self.refresh_UI_callback = None
        self.num_players = len(self.player_manager.players)
        self.current_player_index = 0  # Start with the first player
        self.current_player = self.player_manager.players[self.current_player_index]
        
        self.turn_number = 1
        self.round = 1 # a round passes when every player has taken their turn once
        print(f"Turn number {self.turn_number} of round {self.round} - this is {self.player_manager.players[self.current_player_index].name}'s turn.")

    def handle_menu_actions(self, action, player, district):
        if action == "Create Spy":
            self.spymaster.create_spy(player, district)
            self.refresh_UI_callback()

    def next_turn(self):
        # Logic to advance to the next player's turn
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