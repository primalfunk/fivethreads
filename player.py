class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.name = ""
        self.base_color = (1, 1, 1)
        self.owned_districts = []
        self.spies = []
        self.gold = 250
        self.intel = 250
        self.turn_ap = 0
        self.total_ap = self.calculate_action_points()

    def update_resources(self):
        gold = 0
        intel = 0
        for district in self.owned_districts:
            gold += district.gold
            intel += district.intel
        self.gold = gold
        self.intel = intel
    
    def add_owned_district(self, district):
        self.owned_districts.append(district)
        district.owner = self

    def calculate_action_points(self):
        total_ap = len(self.owned_districts)
        for spy in self.spies:
            total_ap += spy.total_ap
        return total_ap
    
    def total_resources(self):
        gold = 0
        intel = 0
        for district in self.owned_districts:
            gold += district.gold
            intel += district.intel
        return gold + intel
    
    def dilute_player_color(player_color, player, all_players):
        max_resources = max(player.total_resources for player in all_players)
        resource_percentage = player.total_resources / max_resources
        diluted_color = tuple(resource_percentage * component for component in player_color[0])
        return (diluted_color, player_color[1]) 