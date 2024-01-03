class Spy:
    def __init__(self, id, district):
        self.id = id
        self.name = "" # we'll generate a real good one
        self.district = district # every spy has a district they're in
        self.owner = None # always a player object, tells you whose side a spy is on at a given moment
        self.level = 1 # spies can have their levels raised by collecting enough experience
        self.total_ap = 1
        self.experience = 0 # collect experience by performing a variety of spy actions
        self.type = 'living' # the default spy type of five, a swiss army knife of function depending on the context - living, local, inside, reverse, and dead

