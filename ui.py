from action_manager import ActionManager
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Line, Mesh, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.uix.label import Label
from kivy.graphics.context_instructions import PushMatrix, PopMatrix, Translate
from kivy.uix.popup import Popup
from main_menu import MainMenu
from map_tools import Border, MapBorder, DistrictLabel, DistrictWidget, NonClickableImage
import numpy as np
from shapely.geometry import Point

class UI(Widget):
    def __init__(self, screen_size, districts, player_manager, **kwargs):
        super(UI, self).__init__(**kwargs)
        self.districts = districts
        self.screen_size = screen_size
        self.screen_width, self.screen_height = self.screen_size
        self.map_border = self.create_map_border()
        self.player_manager = player_manager
        self.current_player = self.player_manager.players[0] 
        self.main_menu = MainMenu(self, self.current_player.owned_districts[0], self.districts)
        Clock.schedule_once(self.setup_backgrounds)

    def setup_map_elements(self):
        self.map_border_widget = MapBorder(self.map_border)
        self.add_widget(self.map_border_widget)

        for district in self.districts:
            district_widget = DistrictWidget(district, self.map_border, self.shrink_polygons)
            self.add_widget(district_widget)

            label_widget = DistrictLabel(district, self.map_border)
            self.add_widget(label_widget)
    
    def setup_backgrounds(self, dt):
        self.setup_skies()
        self.setup_buildings()
        self.setup_map_back()
        self.redraw_UI() 

    def setup_skies(self):
        self.skies_img = NonClickableImage(source='images/skies.png', keep_ratio=False, allow_stretch=True)
        self.skies_img.size = (self.screen_width * 4, self.screen_height)
        self.skies_img.pos = (-self.screen_width * 3, 0)  # Set the initial position
        self.add_widget(self.skies_img)
        self.animate_skies()

    def animate_skies(self):
            # Animate to move right
            anim = Animation(x=0, duration=550)  # Adjust the duration as needed
            anim.bind(on_complete=self.reset_skies_position)
            anim.start(self.skies_img)

    def reset_skies_position(self, instance, value):
        self.skies_img.pos = (-self.screen_width * 3, 0)  # Reset to initial position
        self.animate_skies()

    def setup_buildings(self):
        self.buildings_img = NonClickableImage(source='images/buildings.png', keep_ratio=False, allow_stretch=True)
        self.buildings_img.size = (self.screen_width * 4, self.screen_height)
        self.buildings_img.pos = (0, 0)
        self.add_widget(self.buildings_img)
        self.animate_buildings()

    def animate_buildings(self):
        anim = Animation(x=-self.screen_width * 3, duration=300)
        anim.bind(on_complete=self.reset_buildings_position)
        anim.start(self.buildings_img)

    def reset_buildings_position(self, instance, value):
        self.buildings_img.pos = (0, 0)
        self.animate_buildings()

    def setup_map_back(self):
        self.map_back_img = NonClickableImage(source='images/map_back.png', keep_ratio=False, allow_stretch=True)
        self.map_back_img.size = (self.screen_width, self.screen_height)
        self.map_back_img.pos = (0, 0)
        self.add_widget(self.map_back_img)

    def redraw_UI(self):
        # Remove and re-add the map border widget if it exists
        if hasattr(self, 'map_border_widget') and self.map_border_widget.parent:
            self.remove_widget(self.map_border_widget)
        self.map_border_widget = MapBorder(self.map_border)
        self.add_widget(self.map_border_widget)

        # Assuming DistrictWidget and DistrictLabel manage their own drawing and updates
        for district in self.districts:
            district_widget = DistrictWidget(district, self.map_border, self.shrink_polygons, self.transform_coordinates, self.create_mesh_data)
            label_widget = DistrictLabel(district, self.map_border, self.transform_coordinates)
            
            # Remove existing widgets for the district if they exist
            if hasattr(self, f'district_widget_{district.id}') and getattr(self, f'district_widget_{district.id}').parent:
                self.remove_widget(getattr(self, f'district_widget_{district.id}'))
            if hasattr(self, f'label_widget_{district.id}') and getattr(self, f'label_widget_{district.id}').parent:
                self.remove_widget(getattr(self, f'label_widget_{district.id}'))
            
            # Add new widgets for the district
            setattr(self, f'district_widget_{district.id}', district_widget)
            setattr(self, f'label_widget_{district.id}', label_widget)
            self.add_widget(district_widget)
            self.add_widget(label_widget)

    def show_main_menu(self, district):
        action_manager = ActionManager(self.current_player, self.districts)
        self.main_menu.update_actions(action_manager, district)
        if self.main_menu.parent:
            self.main_menu.parent.remove_widget(self.main_menu)
        popup = Popup(title="", separator_height=0, content=self.main_menu, size_hint=(None, None), size=(self.screen_size[0] / 2, self.screen_size[1] / 2))
        self.main_menu.popup = popup
        popup.open()

    def create_map_border(self):
        screen_width, screen_height = self.screen_size
        border_width, border_height = 0.76 * screen_width, 0.76 * screen_height
        x = (screen_width - border_width) / 2
        y = (screen_height - border_height) / 2
        return Border(x, y, border_width, border_height)

    def draw_map_border(self):
        with self.canvas.after:
            Color(1, 1, 1)
            Line(rectangle=(self.map_border.x, self.map_border.y, 
                            self.map_border.width, self.map_border.height), width=2)

    def transform_coordinates(self, coords, border_x, border_y, border_width, border_height):
        screen_width, screen_height = self.screen_size
        transformed_coords = []
        for x, y in coords:
            scaled_x = (x / screen_width) * border_width + border_x
            scaled_y = (y / screen_height) * border_height + border_y
            transformed_coords.extend([scaled_x, scaled_y])
        return transformed_coords
    
    def shrink_polygons(self, coords, shrink_percentage=0.004):
        centroid_x, centroid_y = np.mean(coords, axis=0)
        shrunk_coords = []
        shrink_amount = self.screen_width * shrink_percentage
        for x, y in coords:
            direction_x = centroid_x - x
            direction_y = centroid_y - y
            distance = np.sqrt(direction_x**2 + direction_y**2)
            if distance != 0:
                direction_x /= distance
                direction_y /= distance
            new_x = x + direction_x * shrink_amount
            new_y = y + direction_y * shrink_amount
            shrunk_coords.append((new_x, new_y))
        return shrunk_coords
    
    def create_mesh_data(self, coords):
        vertices = []
        indices = []
        for i in range(0, len(coords), 2):  # Step through coords two at a time
            x, y = coords[i], coords[i + 1]
            vertices.extend([x, y, 0, 0])  # (x, y, u, v) for Mesh vertices
            indices.append(i // 2)
        return vertices, indices

    def on_touch_down(self, touch):
        touched_district = self.get_touched_district(touch)
        if touched_district:
            touched_district.original_color = touched_district.color  # Save original color
            touched_district.color = (0.5, 0.5, 0.5, 1)  # Set to grey
            self.redraw_UI()
        return super(UI, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        touched_district = self.get_touched_district(touch)
        if touched_district:
            touched_district.color = touched_district.original_color  # Revert to original color
            self.redraw_UI()
            self.main_menu.set_selected_district(touched_district)  # Update selected district
            self.show_main_menu(touched_district)
        return super(UI, self).on_touch_up(touch)

    def get_touched_district(self, touch):
        transformed_touch_point = Point(self.reverse_transform_coordinates(touch.pos))
        for district in self.districts:
            if district.polygon.contains(transformed_touch_point):
                return district
        return None

    def reverse_transform_coordinates(self, touch_pos):
        touch_x, touch_y = touch_pos
        border_x, border_y, border_width, border_height = self.map_border.x, self.map_border.y, self.map_border.width, self.map_border.height
        scaled_x = (touch_x - border_x) / border_width * self.screen_size[0]
        scaled_y = (touch_y - border_y) / border_height * self.screen_size[1]
        return scaled_x, scaled_y

    def change_district_color(self, district, new_color):
        district.touched_color = district.color  # Store the original color
        district.color = new_color
        self.update_district_visual(district)

    def revert_district_color(self, district):
        district.color = district.touched_color  # Revert to original color
        self.update_district_visual(district)

    def is_point_in_polygon(self, x, y, polygon):
        return polygon.contains(Point(x, y))