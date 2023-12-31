class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.name = ""
        self.color = (1, 1, 1)
        self.owned_districts = []
        self.spies = []
        self.gold = 100
        self.turn_ap = 0
        self.total_ap = self.calculate_action_points()

    def add_owned_district(self, district):
        self.owned_districts.append(district)
        district.owner = self

    def calculate_action_points(self):
        total_ap = len(self.owned_districts)
        for spy in self.spies:
            total_ap += spy.total_ap
        return total_ap