from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')  # Set to 'auto' for full screen or '0' for windowed mode

from kivy.app import App
from kivy.core.window import Window
from setup import GameSetup
from ui import UI

class FiveThreads(App):
    def build(self):
        screen_size = Window.size
        num_players = 2  # Set the number of players
        num_districts = 40
        # Initialize the game with players and districts
        self.game_setup = GameSetup(num_players, num_districts, screen_size)

        self.ui = UI(screen_size, self.game_setup)
        # Giving the GameState a callback to update the screen
        self.game_setup.spymaster.ui_refresh_callback = self.ui.redraw_UI
        self.game_setup.game_state.refresh_UI_callback = self.ui.redraw_UI

        return self.ui

if __name__ == '__main__':
    FiveThreads().run()