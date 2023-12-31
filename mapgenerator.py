import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, box

class MapGenerator:
    @staticmethod
    def generate_voronoi_polygons(screen_width, screen_height, num_districts):
        central_box_width = screen_width
        central_box_height = screen_height
        central_box_x = 0
        central_box_y = 0

        # Generate points within the central box
        points = MapGenerator.distribute_points(central_box_width, central_box_height, num_districts - 4)
        points[:, 0] += central_box_x
        points[:, 1] += central_box_y

        # Add additional points along the borders
        border_points = MapGenerator.add_border_points(central_box_x, central_box_y, central_box_width, central_box_height)
        points = np.vstack([points, border_points])

        vor = Voronoi(points)
        central_box = box(central_box_x, central_box_y, central_box_x + central_box_width, central_box_y + central_box_height)
        polygons = []

        for region_index in vor.point_region:
            region = vor.regions[region_index]
            if -1 not in region and region:
                polygon_points = [vor.vertices[i] for i in region]
                polygon = Polygon(polygon_points)
                if len(polygon.exterior.coords) >= 5:
                    clipped_polygon = polygon.intersection(central_box)
                    polygons.append(clipped_polygon)

        return polygons

    @staticmethod
    def distribute_points(width, height, num_points):
        points = np.random.rand(num_points, 2)
        points[:, 0] *= width
        points[:, 1] *= height
        return points

    @staticmethod
    def add_border_points(x, y, width, height, num_points=4):
        # Add points at the corners of the border box
        return np.array([[x, y], [x + width, y], [x, y + height], [x + width, y + height]])
