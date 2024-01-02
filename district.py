import colorsys
import random

class District:
    def __init__(self, id, polygon):
        self.id = id
        self.polygon = polygon # This shape must be retained for neighbor calculation and creation of touch up/down methods
        self.name = "" # To be determined later
        self.neighbors = [] # A list of all of the districts which share a border with this district instance
        self.owner = None
        self.base_color = self.generate_base_color()
        self.color = self.base_color # default
        self.border_color = self.base_color
        self.population = 0
        self.gold = 0
        self.intel = 0
        self.touched_color = None
        self.spies = []
        self.spy_types = set()
        self.level = 0

    def get_spy_types(self):
        self.spy_types = set()
        for spy in self.spies:
            self.spy_types.add(spy.type)
        for type in list(self.spy_types):
            print(f"Spy in District.spy_types: {type}")
        return list(self.spy_types)

    def generate_base_color(self):
        base_hues = {
            'green': (0.25, 0.45),   # Hues in green spectrum
            'brown': (0.05, 0.1),    # Hues in brown spectrum
            'orange': (0.05, 0.15)   # Hues in orange spectrum
        }
        color_type = random.choice(list(base_hues.keys()))
        hue_range = base_hues[color_type]
        hue = random.uniform(*hue_range)
        saturation = random.uniform(0.5, 0.7)  # Medium to high saturation
        lightness = random.uniform(0.3, 0.5)   # Medium lightness
        return colorsys.hls_to_rgb(hue, lightness, saturation)

    def dilute_color(self):
        # Calculate the percentage based on gold and intelligence
        percentage = max(0, min((self.gold + self.intel) / 500, 1))

        # Convert base_color to a lighter shade
        lightened_color = tuple(percentage * component + (1 - percentage) * 0.8 for component in self.base_color)
        return lightened_color