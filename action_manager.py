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

        if self.can_embed_spy(district):
            actions.append("Embed Spy")

        return actions

    def has_eligible_spies_for_moving(self, district):
        # Check if there are eligible spies in any of the neighboring districts
        for neighbor in district.neighbors:
            dist = self.districts[neighbor]
            for spy in dist.spies:
                if spy.owner == self.player and spy.type in ['living', 'inside', 'reverse', 'dead']:
                    return True
        return False
    
    def get_eligible_spies_for_action(self, action, district):
        eligible_spies = []
        if action == "Move Spy":
            for neighbor in district.neighbors:
                dist = self.districts[neighbor]
                for spy in dist.spies:
                    if spy.owner == self.player and spy.type in ['living', 'inside', 'reverse', 'dead']:
                        eligible_spies.append(spy)
        elif action == "Embed Spy":
            for spy in district.spies:
                if spy.owner == self.player and spy.type == 'living':
                    eligible_spies.append(spy)
        return eligible_spies
    
    def can_embed_spy(self, district):
        if district.owner is None:  # Assuming None represents Neutral
            for spy in district.spies:
                if spy.owner == self.player and spy.type == 'living':
                    return True
        return False