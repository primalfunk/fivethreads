

class ActionManager:
    def __init__(self, player, districts):
        self.player = player
        self.districts = districts

    def get_actions_for_district(self, district):
        if district.owner == self.player:
            # Return a list of actions based on district state and ownership
            return ["Create Spy"]
        else:
            return []