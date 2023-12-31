from district import District
import itertools
import json
from mapgenerator import MapGenerator
import networkx as nx
import numpy as np
import random

class DistrictManager:
    def __init__(self, screen_size, players, num_districts):
        self.screen_size = screen_size
        self.num_players = len(players)
        self.players = players
        self.num_districts = num_districts
        self.districts = self.generate_districts()
        self.identify_neighbors()
        self.county_name = ""
        self.name_districts()
        self.generate_district_stats()
        # need the Player objects to finish with color assignment
        self.assign_initial_districts()
        self.assign_colors_to_districts()

    def calculate_distance(self, district1, district2):
        x1, y1 = district1.polygon.centroid.coords[0]
        x2, y2 = district2.polygon.centroid.coords[0]
        return np.linalg.norm(np.array([x1, y1]) - np.array([x2, y2]))

    def get_map_centroid(self):
        all_coords = [district.polygon.centroid.coords[0] for district in self.districts]
        centroid = np.mean(all_coords, axis=0)
        return tuple(centroid)

    def identify_edge_districts(self):
        centroid = self.get_map_centroid()
        max_distance = 0
        edge_districts = []

        for district in self.districts:
            x, y = district.polygon.centroid.coords[0]
            distance = np.linalg.norm(np.array((x, y)) - np.array(centroid))

            if distance > max_distance:
                max_distance = distance
                edge_districts = [district]
            elif distance == max_distance:
                edge_districts.append(district)

        return edge_districts

    def assign_initial_districts(self):
        print(f"called assign_initial_districts")
        initial_districts = self.select_initial_owned_districts(len(self.players))
        for player, district in zip(self.players, initial_districts):
            player.add_owned_district(district)
            district.owner = player # pass the whole player object as district owner

    def generate_districts(self):
        width, height = self.screen_size
        voronoi_polygons = MapGenerator.generate_voronoi_polygons(width, height, self.num_districts)
        return [District(i + 68, polygon) for i, polygon in enumerate(voronoi_polygons)]

    def generate_district_stats(self):
        for district in self.districts:
            district.population = random.randint(1000, 20000)
            district.gold = district.population // 11 + random.randint(-9, 9)
            district.intel = int(district.gold * 1.5 + random.randint(-9, 9))
    
    def load_county_data(self):
        with open('json/counties.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data

    def select_random_county(self):
        counties_data = self.load_county_data()
        random_county = random.choice(list(counties_data.keys()))
        self.county_name = random_county
        self.city_names = counties_data[random_county]

    def name_districts(self):
        if self.county_name == "":
            self.select_random_county()

        for district in self.districts:
            if self.city_names:  # Check if there are still names available
                district.name = random.choice(self.city_names)
                self.city_names.remove(district.name)  # Ensure uniqueness
            else:
                print("Warning: Ran out of unique city names.")
                district.name = f"District {district.id}"  # Fallback name

    def identify_neighbors(self):
        for i, district in enumerate(self.districts):
            for j, other_district in enumerate(self.districts):
                if i != j and district.polygon.touches(other_district.polygon):
                    district.neighbors.append(other_district.id)

    def calculate_hop_distance(self, start_district, end_district):
        if start_district.id == end_district.id:
            return 0  # No distance between the same district

        visited = set()
        queue = [(start_district, 0)]

        while queue:
            current_district, distance = queue.pop(0)

            if current_district.id == end_district.id:
                return distance

            visited.add(current_district.id)

            for neighbor_id in current_district.neighbors:
                neighbor_district = next((d for d in self.districts if d.id == neighbor_id), None)
                if neighbor_district and neighbor_district.id not in visited:
                    queue.append((neighbor_district, distance + 1))

        return float('inf') 

    def calculate_average_hop_distance(self, candidate, existing_player_districts):
        total_distance = 0
        for player_district in existing_player_districts:
            distance = self.calculate_hop_distance(candidate, player_district)
            total_distance += distance
        return total_distance / len(existing_player_districts)

    def is_at_least_n_hops_away(self, candidate, existing_player_districts):
        for player_district in existing_player_districts:
            if self.calculate_hop_distance(candidate, player_district) < 3:
                return False
        return True

    def select_initial_owned_districts(self, num_players):
        edge_districts = self.identify_edge_districts()
        selected_districts = [random.choice(edge_districts)]
        print(f"Initial edge district selected: {selected_districts[0].id}")

        while len(selected_districts) < num_players:
            suitable_candidates = [d for d in self.districts if self.is_at_least_n_hops_away(d, selected_districts)]

            if suitable_candidates:
                best_candidate = random.choice(suitable_candidates)
                selected_districts.append(best_candidate)
                print(f"Selected District {best_candidate.id}")
            else:
                print("No suitable candidate found. Consider revising the logic or input data.")
                break

        # Print selected districts and their neighbors
        for district in selected_districts:
            neighbors = ', '.join(str(neighbor_id) for neighbor_id in district.neighbors)
            print(f"Player District {district.id}: Neighbors = {neighbors}")

        return selected_districts

    def calculate_path_length(self, start_district, end_district):
        # Initialize a queue for BFS and a set to track visited districts
        queue = [(start_district, 0)]  # Each element is a tuple (district, distance)
        visited = set()

        while queue:
            current_district, distance = queue.pop(0)

            # Check if we have reached the end district
            if current_district.id == end_district.id:
                return distance

            # Mark the current district as visited
            visited.add(current_district.id)

            # Add unvisited neighbors to the queue
            for neighbor_id in current_district.neighbors:
                # Check if neighbor_id is a valid index in self.districts
                if neighbor_id >= 0 and neighbor_id < len(self.districts):
                    neighbor_district = self.districts[neighbor_id]
                    if neighbor_district.id not in visited:
                        queue.append((neighbor_district, distance + 1))
                else:
                    # Handle invalid neighbor_id, possibly log a warning or error
                    print(f"Warning: Invalid neighbor ID {neighbor_id} for district ID {current_district.id}")

        # Return a large number if no path is found
        return float('inf')

    def calculate_total_neighbors(self, district_combination):
        total_neighbors = 0
        for i, district in enumerate(district_combination):
            for other_district in district_combination[i+1:]:
                neighbor_union = len(set(district.neighbors).union(set(other_district.neighbors)))
                total_neighbors += neighbor_union
                print(f"Districts {district.id} and {other_district.id} have {neighbor_union} neighbors in total.")
        return total_neighbors

    def assign_colors_to_districts(self):
        player_colors = self.generate_player_colors(self.num_players)
        color_palette = self.generate_color_palette(len(self.districts))

        for district in self.districts:
            if district.owner is None:
                color_scheme = random.choice(color_palette)
                self.set_district_color(district, color_scheme["background"], color_scheme["border"])
                color_palette.remove(color_scheme)
            else:
                player_color = random.choice(player_colors)
                complementary_color = self.find_complementary(player_color)
                self.set_district_color(district, player_color, complementary_color)
                player_colors.remove(player_color)

    def generate_color_pairs(self):
        primary_colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]  # Red, Green, Blue
        secondary_colors = [(0, 1, 1), (1, 0, 1), (1, 1, 0)]  # Cyan, Magenta, Yellow
        tertiary_colors = [(1, 0.5, 0), (0.5, 1, 0), (0, 1, 0.5), (0, 0.5, 1), (0.5, 0, 1), (1, 0, 0.5)]  # Orange, Chartreuse, Spring Green, Azure, Violet, Rose
        all_colors = primary_colors + secondary_colors + tertiary_colors
        color_pairs = []
        for color in all_colors:
            complementary_color = self.find_complementary(color)
            color_pairs.append((color, complementary_color))

        return color_pairs

    def generate_player_colors(self, num_players):
        color_pairs = self.generate_color_pairs()
        player_colors = []
        for i in range(num_players):
            player_color, _ = color_pairs[i]
            player_colors.append(player_color)
        return player_colors

    def generate_color_palette(self, num_colors):
        def generate_light_color():
            return (random.uniform(0.7, 1), random.uniform(0.7, 1), random.uniform(0.7, 1), 1)

        def darken_color(color):
            return tuple(max(component - 0.2, 0) for component in color[:-1]) + (1,)

        return [{"background": generate_light_color(), "border": (0.8, 0.8, 0.8)} for _ in range(num_colors)]
    
    def set_district_color(self, district, background_color, border_color):
        district.color = background_color
        district.border_color = border_color
        print(f"Set color for district {district.name} id {district.id}")

    def find_complementary(self, color):
        return tuple(1 - c for c in color)

