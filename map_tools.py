from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Line, Mesh, Rectangle
from kivy.uix.image import Image


class Border:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def is_centered(self, screen_size):
        screen_width, screen_height = screen_size
        centered_x = (screen_width - self.width) / 2
        centered_y = (screen_height - self.height) / 2
        return self.x == centered_x and self.y == centered_y


class MapBorder(Widget):
    def __init__(self, border, **kwargs):
        super(MapBorder, self).__init__(**kwargs)
        self.border = border
        self.draw_border()

    def draw_border(self):
        with self.canvas:
            Color(1, 1, 1)
            Line(rectangle=(self.border.x, self.border.y, 
                            self.border.width, self.border.height), width=2)


class NonClickableImage(Image):
    def on_touch_down(self, touch):
        # Do nothing and return True to consume the touch event
        return True

    def on_touch_move(self, touch):
        # Optionally override if needed
        return True

    def on_touch_up(self, touch):
        # Optionally override if needed
        return True


class DistrictWidget(Widget):
    def __init__(self, district, map_border, shrink_polygons, transform_coordinates, create_mesh_data, **kwargs):
        super(DistrictWidget, self).__init__(**kwargs)
        self.district = district
        self.map_border = map_border
        self.shrink_polygons = shrink_polygons
        self.transform_coordinates = transform_coordinates
        self.create_mesh_data = create_mesh_data
        self.draw_district()

    def draw_district(self):
        border_x, border_y, border_width, border_height = self.map_border.x, self.map_border.y, self.map_border.width, self.map_border.height
        original_coords = self.district.polygon.exterior.coords
        shrunk_coords = self.shrink_polygons(original_coords)
        transformed_coords = self.transform_coordinates(shrunk_coords, border_x, border_y, border_width, border_height)
        with self.canvas:
            Color(*self.district.color)
            vertices, indices = self.create_mesh_data(transformed_coords)
            Mesh(vertices=vertices, indices=indices, mode='triangle_fan')
            Color(*self.district.border_color)
            Line(points=transformed_coords, width=2, close=True)


class DistrictLabel(Widget):
    def __init__(self, district, map_border, transform_coordinates, font_path='fonts/russo.ttf', padding=10, **kwargs):
        super(DistrictLabel, self).__init__(**kwargs)
        self.district = district
        self.map_border = map_border
        self.transform_coordinates = transform_coordinates
        self.font_path = font_path
        self.padding = padding

        # Setup label
        self.label = Label(font_size=24 if district.owner is not None else 14,
                           color=(0, 0, 0, 1) if district.owner is not None else (0.5, 0.5, 0.5, 1),
                           text=district.name + f" ({district.owner.name})" if district.owner else district.name,
                           font_name=self.font_path,
                           size_hint=(None, None))
        self.label.texture_update()  # Update texture size based on text
        self.add_widget(self.label)

        # Initialize the rectangle for the background
        with self.canvas.before:
            Color(1, 1, 1, 0.7)  # Light color with some transparency
            self.rect = Rectangle()

        self.update_label()

    def update_label(self):
        centroid = self.district.polygon.centroid.coords[0]
        transformed_centroids = self.transform_coordinates([centroid], self.map_border.x, self.map_border.y, self.map_border.width, self.map_border.height)
        self.size = (self.label.texture_size[0] + self.padding, self.label.texture_size[1] + self.padding)
        self.pos = (transformed_centroids[0] - self.width / 2, transformed_centroids[1] - self.height / 2)

        self.label.size = self.label.texture_size
        self.label.pos = (self.x + self.padding / 2, self.y + self.padding / 2)
        self.rect.size = self.size
        self.rect.pos = self.pos

    def on_size(self, *args):
        self.rect.size = self.size
        self.label.size = self.label.texture_size
        self.label.pos = (self.x + self.padding / 2, self.y + self.padding / 2)

    def on_pos(self, *args):
        self.rect.pos = self.pos
        self.label.pos = (self.x + self.padding / 2, self.y + self.padding / 2)