from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

class ModernButton(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal_color = [0.5, 0.5, 0.5, 1]  # Default color
        self.background_down_color = [0.3, 0.3, 0.3, 1]  # Color when pressed
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            current_color = self.background_down_color if self.state == 'down' else self.background_normal_color
            Color(*current_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

    def on_press(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_down_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

    def on_release(self):
        self.update_graphics()