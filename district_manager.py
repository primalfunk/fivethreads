import colorsys
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

    def refresh_district_colors(self):
        for district in self.districts:
            if district.owner is None:
                district.color = district.dilute_color()
            else:
                player = district.owner
                district.color = self.dilute_player_color(player.base_color, player, self.players)

    def assign_colors_to_districts(self):
        player_color_pairs = self.generate_player_colors(self.num_players)
        
        # Assign each player a unique color pair
        for player, color_pair in zip(self.players, player_color_pairs):
            player.base_color, player.border_color = color_pair

        for district in self.districts:
            if district.owner is None:
                base_color = district.generate_base_color()
                scaled_color = district.dilute_color()
                self.set_district_color(district, scaled_color, (0.7, 0.7, 0.7))
            else:
                player = district.owner
                player_color = self.dilute_player_color(player.base_color, player, self.players)
                self.set_district_color(district, player_color, player.border_color)

    def set_district_color(self, district, background_color, border_color):
        district.color = background_color
        district.border_color = border_color

    def dilute_player_color(self, player_color, player, all_players):
        max_resources = max(player.total_resources() for player in all_players)

        # Ensure max_resources is at least 1 to avoid division by zero
        max_resources = max(1, max_resources)

        # Calculate resource percentage and ensure it's between 0 and 1
        resource_percentage = player.total_resources() / max_resources
        resource_percentage = max(0, min(resource_percentage, 1))

        # Apply dilution to the RGB components of the color
        diluted_color = tuple(resource_percentage * component for component in player_color)
        
        # Ensure color values are within the range 0 to 1
        diluted_color = tuple(min(max(component, 0), 1) for component in diluted_color)

        return diluted_color

    def generate_player_colors(self, num_players):
        hue_step = 1.0 / num_players
        player_colors = []
        for i in range(num_players):
            hue = i * hue_step
            saturation = 0.7  # Fixed saturation for distinct colors
            lightness = 0.5   # Fixed lightness
            background_color = colorsys.hls_to_rgb(hue, lightness, saturation)
            border_color = colorsys.hls_to_rgb(hue, lightness, 1)  # Full brightness for border
            player_colors.append((background_color, border_color))
        return player_colors

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
        initial_districts = self.select_initial_owned_districts(len(self.players))
        for player, district in zip(self.players, initial_districts):
            player.add_owned_district(district)
            district.owner = player # pass the whole player object as district owner

    def generate_districts(self):
        width, height = self.screen_size
        voronoi_polygons = MapGenerator.generate_voronoi_polygons(width, height, self.num_districts)
        return [District(i + 68, polygon) for i, polygon in enumerate(voronoi_polygons)]
    
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

        while len(selected_districts) < num_players:
            suitable_candidates = [d for d in self.districts if self.is_at_least_n_hops_away(d, selected_districts)]

            if suitable_candidates:
                best_candidate = random.choice(suitable_candidates)
                selected_districts.append(best_candidate)
            else:
                break

        # Print selected districts and their neighbors
        for district in selected_districts:
            neighbors = ', '.join(str(neighbor_id) for neighbor_id in district.neighbors)

        return selected_districts



    def generate_district_stats(self):
        for district in self.districts:
            district.population = random.randint(1000, 10000)
            district.gold = 125 + random.randint(0, 110)
            district.intel = 125 + random.randint(0, 110)

    def calculate_total_neighbors(self, district_combination):
        total_neighbors = 0
        for i, district in enumerate(district_combination):
            for other_district in district_combination[i+1:]:
                neighbor_union = len(set(district.neighbors).union(set(other_district.neighbors)))
                total_neighbors += neighbor_union
        return total_neighbors
