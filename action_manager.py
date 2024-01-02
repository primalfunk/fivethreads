class ActionManager:
    def __init__(self, player, districts):
        self.player = player
        self.districts = districts

    def get_actions_for_district(self, district):
        actions = []
        if district.owner == self.player:
            # Always allow creating a spy
            actions.append("Create Spy")

        # Check for eligible spies for moving in neighboring districts
        if self.has_eligible_spies_for_moving(district):
            actions.append("Move Spy")

        return actions

    def has_eligible_spies_for_moving(self, district):
        # Check if there are eligible spies in any of the neighboring districts
        for neighbor in district.neighbors:
            dist = self.districts[neighbor]
            for spy in dist.spies:
                if spy.owner == self.player and spy.type in ['living', 'inside', 'reverse', 'dead']:
                    return True
        return False