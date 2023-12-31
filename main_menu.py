from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Mesh, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line
from modern_button import ModernButton

class MainMenu(BoxLayout):
    def __init__(self, ui, district, districts, **kwargs):
        super().__init__(**kwargs)
        self.ui = ui
        self.popup = None
        self.graphics_ready = False
        self.districts = districts
        if district is not None:
            self.selected_district = district
        else:
            self.selected_district = self.districts[0] # default to some specific district
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        Clock.schedule_once(self.setup_layout)

    def set_selected_district(self, district):
            self.selected_district = district
            self.populate_general_info()  

    def dismiss_popup(self, instance):
        if self.popup:
            self.popup.dismiss()

    def check_graphics_update(self):
        if not self.graphics_ready:
            self.graphics_ready = True
            Clock.schedule_once(self._update_graphics, 0.1)

    def setup_layout(self, dt):
        self.general_info_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.25))
        self.central_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        self.system_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.25))

        self.add_widget(self.general_info_layout)
        self.add_widget(self.central_layout)
        self.add_widget(self.system_layout)
        # Print layout sizes and positions after setup
        print("General Info Layout:", self.general_info_layout.size, self.general_info_layout.pos)
        print("Central Layout:", self.central_layout.size, self.central_layout.pos)
        print("System Layout:", self.system_layout.size, self.system_layout.pos)
        
        self.populate_general_info()
        self.populate_system_area()
    
    def populate_general_info(self):
        self.general_info_layout.clear_widgets()  # Clear existing widgets
        self.general_info_layout.size_hint_y = None
        self.general_info_layout.height = self.ui.screen_height // 10
        self.general_info_layout.pos_hint = {'top': 0.9}

        if self.selected_district:
            # Check if owner is not None before accessing its name
            owner_name = self.selected_district.owner.name if self.selected_district.owner else "Neutral"
            spy_network_level = self.selected_district.level
            self.general_info_layout.add_widget(Label(text=f"District ID: {self.selected_district.id}"))
            self.general_info_layout.add_widget(Label(text=f"District Name: {self.selected_district.name}"))
            self.general_info_layout.add_widget(Label(text=f"Owner: {owner_name}"))
            self.general_info_layout.add_widget(Label(text=f"Spy Network Level: {spy_network_level}"))
            self.general_info_layout.add_widget(Label(text=f"Gold: {self.selected_district.gold}"))
            self.general_info_layout.add_widget(Label(text=f"Intel: {self.selected_district.intel}"))
            print("Populated General Info with Widgets")
    
    def populate_system_area(self):
        self.system_layout.clear_widgets()
        self.system_layout.size_hint_y = None
        self.system_layout.height = self.ui.screen_height // 20
        button_width_hint = 0.25
        empty_widget_width_hint = (1/3 - button_width_hint / 2)
        self.system_layout.add_widget(Widget(size_hint_x=empty_widget_width_hint))
        self.system_layout.add_widget(ModernButton(text="Options", size_hint=(button_width_hint, None), height=30, pos_hint={'center_y': 0.5}))
        self.system_layout.add_widget(Widget(size_hint_x=empty_widget_width_hint * 2))
        close_button = ModernButton(text="Close", size_hint=(button_width_hint, None), height=30, pos_hint={'center_y': 0.5})
        close_button.bind(on_press=self.dismiss_popup)
        self.system_layout.add_widget(close_button)
        self.system_layout.add_widget(Widget(size_hint_x=empty_widget_width_hint))

    def populate_central_area(self, action_manager, selected_district):
        self.central_layout.clear_widgets()  # Clear existing widgets

        # Define padding and spacing values
        padding_value = 10  # Space around the edges inside the BoxLayout
        spacing_value = 15  # Space between the buttons

        # Create a BoxLayout for buttons inside the ScrollView
        button_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=spacing_value, padding=[padding_value, padding_value, padding_value, 0])
        button_layout.bind(minimum_height=button_layout.setter('height'))

        # Get actions and populate buttons
        actions = action_manager.get_actions_for_district(selected_district)
        if not actions:
            # Add a button indicating no valid actions
            no_action_button = Button(text="No valid actions", size_hint=(1, None), height=40, disabled=True)
            button_layout.add_widget(no_action_button)
        else:
            # Add a title button for district actions
            title_button = Button(text="District Actions", size_hint=(1, None), height=40, disabled=True)
            button_layout.add_widget(title_button)

            for action in actions:
                button = Button(text=action, size_hint=(1, None), height=40)
                button_layout.add_widget(button)

        # Create a ScrollView and add the button layout to it
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(button_layout)

        # Add ScrollView to the central layout
        self.central_layout.add_widget(scroll_view)

    def update_graphics(self, *args):
        # Schedule the update after a short delay
        Clock.schedule_once(self._update_graphics, 0.1)
    
    def _update_graphics(self, *args):
        print("Executing _update_graphics")
        self.canvas.after.clear()
        with self.canvas.after:
            # Background colors
            Color(1, 0, 0, 0.5)  # Red semi-transparent background for general_info_layout
            Rectangle(pos=self.general_info_layout.pos, size=self.general_info_layout.size)
            
            Color(0, 0, 1, 0.5)  # Blue semi-transparent background for system_layout
            Rectangle(pos=self.system_layout.pos, size=self.system_layout.size)

            # Section borders
            Color(0.6, 0.6, 0.6, 1)  # Adjust color as needed
            self.draw_section_border(self.central_layout)
            self.draw_section_border(self.system_layout)
        print("Updated Graphics - Drawing backgrounds and borders")

    def draw_section_border(self, section_widget):
        with self.canvas.after:
            Color(0.6, 0.6, 0.6, 1)  # Adjust color as needed
            Line(rectangle=(section_widget.x, section_widget.y, section_widget.width, section_widget.height), width=1.5)

    def update_actions(self, action_manager, selected_district):
        print(f"Called mainmenu.update_actions()")
        self.selected_district = selected_district
        self.populate_central_area(action_manager, selected_district)