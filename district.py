class District:
    def __init__(self, id, polygon):
        self.id = id
        self.polygon = polygon # This shape must be retained for neighbor calculation and creation of touch up/down methods
        self.name = "" # To be determined later
        self.neighbors = [] # A list of all of the districts which share a border with this district instance
        self.owner = None
        self.color = (0, 0, 0)
        self.border_color = (0.3, 0.3, 0.3)
        self.population = 0
        self.gold = 0
        self.intel = 0
        self.touched_color = None
        self.spies = []
        self.level = 0