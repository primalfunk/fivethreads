import json
from message_popup import MessagePopup
import random
from spy import Spy

class SpyMaster:
    def __init__(self, players, districts):
        self.ui_refresh_callback = None
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

    def create_spy(self, player, district):
        # Generate a unique ID and name for the spy
        spy_id = len(self.spies) + 68
        spy_name = self.generate_spy_name()
        new_spy = Spy(spy_id, district)
        new_spy.name = spy_name
        new_spy.owner = player
        new_spy.type = 'living'
        new_spy.district = district
        self.spies.append(new_spy)
        player.spies.append(new_spy)
        district.spies.append(new_spy)
        self.ui_refresh_callback()
        spy_details = f"Spy created!\nName: {new_spy.name}\nID: {new_spy.id}\nDistrict: {new_spy.district.name}"
        message_popup = MessagePopup(message=spy_details)
        message_popup.open()

    def generate_name(self):
        first_name = random.choice(self.first_names)
        if random.randint(0, 100) < 15 :
            middle_names = [" 'Danger'", " 'the Rocket'", " 'the Tomahawk'", " 'Snake eyes'", " 'Caliber'", " 'Deadshot'", " 'Combo'", " 'the Hammer'", " 'La Prima'", " 'Shorty'", " 'Crazy Eyes'", " 'One-Leg'", " 'Rambo'", " 'Hotdog'", " 'Starbuck'", " 'Alien'", " 'Alien II'", " 'Alien III'", " 'Bob'", " 'Superfly'", " 'Kid Crazy'", " 'Auntie'", " 'Uncle'", " 'Santa Claus'", " 'Husker'", " 'Boomer'", " 'Apollo'", " 'Number Two'", " 'the Saint'", " 'the Nun'", " 'Supersmoove'", " 'Bats'", " 'Superfan'", " of the Clan", "Baby Legs"]
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
        suffixes = ["Jr", "II", "III", "IV", "Sr", "Ph.D", "CPA"]
        if random.random() < 0.15:  # 15% chance
            suffix = random.choice(suffixes)
            name = f"{name} {suffix}"
        return name
    
    def add_second_last_name(self, name):
        if random.random() < 0.06:  # 6% chance
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
            name = self.add_second_last_name(name)
            name = self.add_suffixes(name)
            if name not in spy_names:
                spy_names.append(name)

        return spy_names