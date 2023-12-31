import json
import random
from spy import Spy

class SpyMaster:
    def __init__(self, players, districts):
        self.spies = []
        self.players = players
        self.districts = districts
        self.names = []
        self.load_names()
        self.spy_names = self.generate_spy_names()

    def load_names(self):
        with open('json/names.json', 'r') as f:
            self.first_names = json.load(f)["first_names"]
        with open('json/names.json', 'r') as f:
            self.last_names = json.load(f)["last_names"]

    def create_spy(self, player, district_id):
        # Generate a unique ID and name for the spy
        spy_id = len(self.spies) + 1
        spy_name = self.generate_spy_name()

        # Create new Spy instance
        new_spy = Spy(spy_id, district_id)
        new_spy.name = spy_name
        new_spy.owner = player
        new_spy.district = self.districts[district_id]

        # Add the spy to the SpyMaster's list, player's list, and district's list
        self.spies.append(new_spy)
        print(f"Spy name: {new_spy.name}, id {new_spy.id}")
        player.spies.append(new_spy)
        self.districts[district_id].spies.append(new_spy)

    def generate_name(self):
        first_name = random.choice(self.first_names)
        if random.randint(0, 100) < 5 :
            middle_names = [" 'Danger'", " 'the Rocket'", " 'the Tomahawk'", " 'Snake eyes'", " 'Caliber'", " 'Deadshot'", " 'Combo'", " 'the Hammer'", " 'La Prima'", " 'Shorty'", " 'Crazy Eyes'", " 'One-Leg'", " 'Rambo'", " 'Hotdog'", " 'Starbuck'", " 'Alien'", " 'Alien II'", " 'Alien III'", " 'Bob'", " 'Superfly'", " 'Kid Crazy'", " 'Auntie'", " 'Uncle'", " 'Santa Claus'", " 'Husker'", " 'Boomer'", " 'Apollo'", " 'Number Two'", " 'the Saint'", " 'the Nun'", " 'Supersmoove'", " 'Bats'", " 'Superfan'", " of the Clan"]
            first_name += random.choice(middle_names)
        last_name = random.choice(self.last_names)
        return f"{first_name} {last_name}"
    
    def add_titles(self, name):
        titles = ["Dr.", "Col.", "Capt.", "Maj.", "Lt.", "Sgt.", "Pvt", "Chief", "Officer"]
        if random.random() < 0.25:  # 25% chance
            title = random.choice(titles)
            name = f"{title} {name}"
        return name

    def add_suffixes(self, name):
        suffixes = ["Jr", "II", "III", "IV", "Sr"]
        if random.random() < 0.15:  # 15% chance
            suffix = random.choice(suffixes)
            name = f"{name} {suffix}"
        return name
    
    def add_second_last_name(self, name):
        if random.random() < 0.33:  # 33% chance
            second_last_name = random.choice(self.last_names)
            name = f"{name}-{second_last_name}"
        return name
    
    def generate_spy_name(self):
        random.shuffle(self.spy_names)
        return self.spy_names.pop()

    def generate_spy_names(self, num_names=800):
        spy_names = []
        while len(spy_names) < num_names:
            name = self.generate_name()
            name = self.add_titles(name)
            name = self.add_suffixes(name)
            name = self.add_second_last_name(name)

            if name not in spy_names:
                spy_names.append(name)

        return spy_names