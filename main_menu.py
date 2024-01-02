from action_manager import ActionManager
from kivy.animation import Animation
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# Register the custom font
LabelBase.register(name='Play', fn_regular='fonts/play.ttf')

class MainMenu(RelativeLayout):
    def __init__(self, ui, district, districts, action_callback, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        self.ui = ui
        self.player = self.ui.current_player
        self.action_callback = action_callback
        self.pos = (self.ui.screen_width / 4, self.ui.screen_height / 4)
        self.size = (ui.screen_width / 2, ui.screen_height / 2)
        self.districts = districts
        self.indicator = None
        self.indicator_color = (1, 0.86, 0, 0.8)
        self.selected_district = district if district is not None else districts[0]
        self.action_manager = ActionManager(self.ui.current_player, self.districts)
        self.general_info_labels = []
        self.action_buttons = []
        self.side_buttons = []
        self.width, self.height = self.size
        self.x, self.y = self.pos
        self.background_image = Image(source='images/menu.png', allow_stretch=True, size=self.size)
        self.add_widget(self.background_image)
        Clock.schedule_once(self.setup_layout)

    def set_indicator_color(self):
        district = self.selected_district
        color = None
        if district.owner == self.ui.current_player and len(district.spies) > 0:
            color = (0, 1, 0, 1) # Green for owned and has spies
        elif district.owner == self.ui.current_player and len(district.spies) == 0:
            color = (0, 1, 1, 1) # Cyan for owned and no spies
        elif district.owner != self.ui.current_player and district.owner is not None:
            color = (1, 0, 0, 1) # Red for hostile player
        else:
            color = (1, 0.8, 0, 1) # Yellow for neutral
        self.indicator_color = color

    def update_action_buttons(self):
        for btn in self.action_buttons:
            self.remove_widget(btn)
        self.action_buttons.clear()
        action_area_x = self.width * 0.0341
        action_area_y = self.height * 0.032
        action_area_height = self.height * 0.559
        action_button_x = action_area_x
        action_button_height = action_area_height * 0.1
        selected_color = (0.678, 0.847, 1, 1)  # Light blue
        unselected_color = (0.25, 0.25, 0.25, 1)  # Dark gray
        available_actions = self.get_available_actions_for_district(self.selected_district)
        base_action_text = "Available actions:" if available_actions else "No available actions"
        base_action_button = Button(
            text=base_action_text,
            size_hint=(None, None),
            size=(self.width * 0.795, action_button_height),
            pos=(action_button_x, action_area_y + action_area_height - action_button_height),
            background_color=unselected_color
        )
        self.add_widget(base_action_button)
        self.action_buttons.append(base_action_button)
        if available_actions:
            for index, action in enumerate(available_actions):
                action_button_y = action_area_y + action_area_height - (index + 2) * action_button_height
                action_button = ToggleButton(
                    text=action,
                    selected_color=selected_color,
                    unselected_color=unselected_color,
                    pos=(action_button_x + 1, action_button_y),
                    size_hint=(None, None),
                    size=(self.width * 0.794, action_button_height)
                )
                action_button.bind(on_release=self.handle_action_button_press)
                self.add_widget(action_button)
                self.action_buttons.append(action_button)

    def handle_action_button_press(self, instance):
        if instance.is_selected:
            instance.is_selected = False
            instance.background_color = instance.unselected_color
            # Reset to show available actions
            self.update_action_buttons()
        else:
            for button in self.action_buttons:
                if button != instance and isinstance(button, ToggleButton):
                    button.is_selected = False
                    button.background_color = button.unselected_color
            instance.is_selected = True
            instance.background_color = instance.selected_color
            # If a two-step action is selected, prepare for the second step
            if instance.text in ["Move Spy"]:  # Add other two-step actions here
                self.prepare_for_second_step(instance.text)

    def prepare_for_second_step(self, action):
        if action == "Move Spy":
            self.populate_spies_for_action(action)

    def populate_spies_for_action(self, action):
        # Modify view for the second step
        # Clear current action buttons
        for btn in self.action_buttons:
            self.remove_widget(btn)
        self.action_buttons.clear()

        # Change title to 'Available Spies'
        action_button_y = self.height * 0.032 + self.height * 0.559 - 0.1 * self.height * 0.559
        title_button = Button(
            text="Available Spies",
            size_hint=(None, None),
            size=(self.width * 0.795, 0.1 * self.height * 0.559),
            pos=(self.width * 0.0341, action_button_y),
            background_color=(0.25, 0.25, 0.25, 1)
        )
        self.add_widget(title_button)
        self.action_buttons.append(title_button)

        # Populate spies for the action
        eligible_spies = self.get_eligible_spies_for_action(action)
        for index, spy in enumerate(eligible_spies):
            spy_button_y = action_button_y - (index + 1) * 0.1 * self.height * 0.559
            spy_button = Button(
                text=f"{spy.name} (ID: {spy.id})",
                size_hint=(None, None),
                size=(self.width * 0.794, 0.1 * self.height * 0.559),
                pos=(self.width * 0.0341 + 1, spy_button_y),
                background_color=(0.678, 0.847, 1, 1)  # Light blue
            )
            # Bind action to spy_button here, such as moving the spy
            self.add_widget(spy_button)
            self.action_buttons.append(spy_button)

    def get_eligible_spies_for_action(self, action):
        # Logic to return eligible spies for the given action
        eligible_spies = []
        if action == "Move Spy":
            # Fetch spies eligible for moving
            eligible_spies = [spy for spy in self.selected_district.spies if spy.owner == self.ui.current_player]
        return eligible_spies

    def execute_selected_action(self, instance):
        selected_action_button = next((button for button in self.action_buttons if getattr(button, 'is_selected', False)), None)
        self.dismiss_popup(instance)
        if selected_action_button:
            self.perform_action(selected_action_button)

    def perform_action(self, instance):
        action = instance.text
        print(f"Performing {action} on {self.selected_district.name}")
        self.action_callback(action, self.ui.current_player, self.selected_district)

    def add_side_buttons(self):
        circular_button_diameter = self.height * 0.0857  # 8.57% of the menu's height
        circular_button_x = self.width * 0.905  # 90.5% of the menu's width
        unpressed_color = (0.5, 0.5, 0.5, 0.2)
        colors = {"red": (1, 0, 0, 1),
                  "yellow": (1, 1, 0, 1),
                  "blue": (0, 0.2, 1, 1)}
        circular_button_ys = [
            (self.height * 0.723, "blue"),
            (self.height * 0.566, "yellow"),
            (self.height * 0.221, "red")
        ]
        self.side_buttons = []
        for y, color in circular_button_ys:
            button = CircularButton(
                pressed_color=colors[color],
                unpressed_color=unpressed_color,
                pos=(circular_button_x - circular_button_diameter / 2, y - circular_button_diameter / 2),
                size_hint=(None, None),
                size=(circular_button_diameter, circular_button_diameter)
            )
            if color == "red":
                button.bind(on_release=self.dismiss_popup)
            if color == "blue":
                button.bind(on_release=self.execute_selected_action)
            self.add_widget(button)
            self.side_buttons.append(button)
        self.create_indicator_button(self.indicator_color)

    def dismiss_popup(self, instance):
        # Logic to close the MainMenu popup
        self.ui.main_menu_popup.dismiss()

    def setup_layout(self, *args):
        self.update_general_info_labels()  # Create or update general info labels
        self.update_action_buttons()  # Create or update action buttons
        self.add_side_buttons()  # Create side buttons

    def set_selected_district(self, district):
        self.selected_district = district
        self.update_general_info_labels()  # Update labels for the new district
        self.update_action_buttons()

    def get_available_actions_for_district(self, district):
        return self.action_manager.get_actions_for_district(district)

    def update_general_info_labels(self):
        for label in self.general_info_labels:
            self.remove_widget(label)
        self.general_info_labels = []
        text_area_x = self.width * 0.04  # 3% from the left edge of the MainMenu
        text_area_y = self.height * 0.38  # 38% from the bottom of the MainMenu
        text_area_width = self.width * 0.82  # 82% of the MainMenu's width
        text_area_height = self.height * 0.11  # 11% of the MainMenu's height
        num_columns = 3  # Three columns
        num_rows = 2  # Two rows of labels
        label_width = text_area_width / num_columns
        label_height = text_area_height / (num_rows * 2)  # Times 2 for key-value pairs
        start_y = text_area_y + (self.height / 2) - label_height
        district_info = [
            ("District Name", self.selected_district.name),
            ("District ID", self.selected_district.id),
            ("District Owner", self.selected_district.owner.name if self.selected_district.owner else 'Neutral'),
            ("Spy Network Level", self.selected_district.level),
            ("Player Gold", self.player.gold),
            ("Player Intel", self.player.intel)
        ]
        for index, (key, value) in enumerate(district_info):
            col = index % num_columns
            row = (index // num_columns) * 2  # Multiply by 2 for each key-value pair
            pos_x = text_area_x + (label_width * col)
            pos_key_y = start_y - (row * label_height)
            pos_value_y = pos_key_y - label_height
            key_label = Label(
                text=f"{key}:",
                pos=(pos_x, pos_key_y),
                size_hint=(None, None),
                size=(label_width, label_height),
                text_size=(label_width, None),
                font_name='Play',
                color=get_color_from_hex('#00FF00'),
                valign='middle',
                halign='left'
            )
            self.add_widget(key_label)
            self.general_info_labels.append(key_label)
            value_label = Label(
                text=str(value),
                pos=(pos_x, pos_value_y),
                size_hint=(None, None),
                size=(label_width, label_height),
                text_size=(label_width, None),
                font_name='Play',
                color=get_color_from_hex('#00FF00'),
                valign='middle',
                halign='left'
            )
            self.add_widget(value_label)
            self.general_info_labels.append(value_label)
            additional_line_y = pos_value_y - label_height - 10  # 10 is the space below the second row
            spy_names = ', '.join(spy.name for spy in self.selected_district.spies)
        additional_line_text = f"Known spies in this district: {spy_names}"
        additional_label = Label(
            text=additional_line_text,
            pos=(text_area_x, additional_line_y),
            size_hint=(None, None),
            size=(text_area_width, label_height),
            text_size=(text_area_width, None),
            font_name='Play',
            color=get_color_from_hex('#00FF00'),
            valign='middle',
            halign='left'
        )
        self.add_widget(additional_label)
        self.general_info_labels.append(additional_label)

    def update_graphics(self, *args):
        # This method could be used for any custom drawing or updates needed
        # Currently, it's empty and can be implemented if needed
        pass

    def create_indicator_button(self, color):
        # Remove existing indicator if it exists
        if self.indicator is not None:
            self.remove_widget(self.indicator)
        rect_button_width = self.width * 0.065
        rect_button_height = self.height * 0.04
        rect_button_x = self.width * 0.873
        rect_button_y = self.height * 0.883 - rect_button_height
        self.indicator = RectangularButton(
            base_color=color,
            pos=(rect_button_x, rect_button_y),
            size_hint=(None, None),
            size=(rect_button_width, rect_button_height)
        )
        self.add_widget(self.indicator)
        self.side_buttons.append(self.indicator)


class CircularButton(ButtonBehavior, Widget):
    circle = None
    def __init__(self, pressed_color, unpressed_color, **kwargs):
        super().__init__(**kwargs)
        self.pressed_color = pressed_color
        self.unpressed_color = unpressed_color

        # Draw the initial circle with the unpressed color
        with self.canvas:
            Color(*self.unpressed_color)
            self.circle = Ellipse(size=self.size, pos=self.pos)

    def on_press(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.pressed_color)
            Ellipse(pos=self.pos, size=self.size)

    def on_release(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.unpressed_color)
            Ellipse(pos=self.pos, size=self.size)

    def on_size(self, *args):
        # Update the circle size
        if self.circle:
            self.circle.size = self.size

    def on_pos(self, *args):
        # Update the circle position
        if self.circle:
            self.circle.pos = self.pos


class RectangularButton(Widget):
    rect = None
    def __init__(self, base_color, **kwargs):
        super().__init__(**kwargs)
        self.base_color = base_color
        self.dimmed_color = [c * 0.5 for c in self.base_color]  # Dim the color to 50%
        with self.canvas:
            self.color_instruction = Color(*self.base_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.start_animation()

    def start_animation(self):
        Animation.cancel_all(self.color_instruction, 'rgba')
        # Create an animation that smoothly transitions the color
        anim = Animation(rgba=self.dimmed_color, duration=1) + Animation(rgba=self.base_color, duration=1)
        anim.repeat = True  # Repeat the animation indefinitely
        anim.start(self.color_instruction)

    def on_size(self, *args):
        if self.rect:
            self.rect.size = self.size

    def on_pos(self, *args):
        if self.rect:
            self.rect.pos = self.pos


class ToggleButton(Button):
    rect = None
    def __init__(self, selected_color, unselected_color, **kwargs):
        super().__init__(**kwargs)
        self.selected_color = selected_color
        self.unselected_color = unselected_color
        self.background_normal = ''  # Removes default styling
        self.background_color = self.unselected_color
        self.is_selected = False

    def toggle(self):
        self.is_selected = not self.is_selected
        new_color = self.selected_color if self.is_selected else self.unselected_color
        self.background_color = new_color

    def on_size(self, *args):
        if self.rect:
            self.rect.size = self.size

    def on_pos(self, *args):
        if self.rect:
            self.rect.pos = self.pos