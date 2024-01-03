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