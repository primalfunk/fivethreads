from kivy.uix.popup import Popup
from kivy.uix.label import Label

class MessagePopup(Popup):
    def __init__(self, message, **kwargs):
        super(MessagePopup, self).__init__(**kwargs)
        self.title = 'Message'
        self.content = Label(text=message, font_size='20sp')
        self.size_hint = (0.5, 0.3)  # Adjust as needed
        self.auto_dismiss = True  # Allows dismissal by clicking outside the popup

    def on_touch_down(self, touch):
        # Override the on_touch_down method
        if self.collide_point(*touch.pos):
            # Check if touch is inside the popup
            self.dismiss()  # Dismiss the popup
            return True
        return super(MessagePopup, self).on_touch_down(touch)