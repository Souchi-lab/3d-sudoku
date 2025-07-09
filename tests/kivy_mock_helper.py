import sys
from unittest.mock import MagicMock


# Define MockEventDispatcher outside the function
class MockEventDispatcher(MagicMock):
    pass


# Custom mock for Kivy properties to behave like simple attributes
class SimpleKivyPropertyMock:
    def __init__(self, default_value):
        self._value = default_value

    def __get__(self, instance, owner):
        return self._value

    def __set__(self, instance, value):
        self._value = value


import re


class MockWidget(MagicMock):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        def parse_kivy_size(value):
            if isinstance(value, str) and value.endswith("dp"):
                return int(re.match(r"^(\d+)", value).group(1))
            return int(value)

        self.canvas = MagicMock()
        self.canvas.before = MagicMock()
        self.children = []  # For add_widget
        self.width = parse_kivy_size(kwargs.get("width", 100))  # Default width
        self.height = parse_kivy_size(kwargs.get("height", 100))  # Default height
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.pos = (self.x, self.y)
        self.size = (self.width, self.height)
        self.center_x = self.x + self.width / 2
        self.center_y = self.y + self.height / 2
        for k, v in kwargs.items():  # Store kwargs as attributes
            setattr(self, k, v)

    def add_widget(self, widget):
        self.children.append(widget)

    def remove_widget(self, widget):
        pass

    def clear_widgets(self):
        self.children = []

    def bind(self, **kwargs):
        pass

    def setter(self, name):
        # Mock Kivy's setter method
        return MagicMock()

    def __call__(self, *args, **kwargs):
        return self

    def collide_point(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height


def mock_kivy_modules():
    # Create dummy classes for base Kivy widgets and properties

    # --- Mock kivy.properties ---
    mock_properties = MagicMock()
    mock_properties.PropertyStorage = type("PropertyStorage", (object,), {})
    mock_properties.NumericProperty = lambda default_value=0, **kwargs: default_value
    mock_properties.ListProperty = lambda default_value=[], **kwargs: default_value
    mock_properties.StringProperty = lambda default_value="", **kwargs: default_value
    sys.modules["kivy.properties"] = mock_properties

    # --- Mock kivy.event ---
    mock_event = MagicMock()
    mock_event.EventDispatcher = MockEventDispatcher  # Now MockEventDispatcher is in scope
    sys.modules["kivy.event"] = mock_event

    # --- Mock other Kivy modules ---
    sys.modules["kivy.app"] = MagicMock(App=type("App", (object,), {}))
    sys.modules["kivy.uix.boxlayout"] = MagicMock(BoxLayout=type("BoxLayout", (MockWidget,), {}))
    sys.modules["kivy.uix.label"] = MagicMock(Label=type("Label", (MockWidget,), {}))
    sys.modules["kivy.uix.button"] = MagicMock(Button=type("Button", (MockWidget,), {}))
    sys.modules["kivy.uix.popup"] = MagicMock(Popup=type("Popup", (MockWidget,), {}))
    sys.modules["kivy.uix.widget"] = MagicMock(Widget=MockWidget)
    sys.modules["kivy.uix.slider"] = MagicMock(Slider=type("Slider", (MockWidget,), {}))
    sys.modules["kivy.uix.togglebutton"] = MagicMock(ToggleButton=type("ToggleButton", (MockWidget,), {}))

    # Enhanced ScreenManager Mock
    class MockScreen(MockWidget):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.name = kwargs.get("name")  # Screens have a name

    class MockScreenManager(MockWidget):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self._screens = {}
            self._current = "level_select"  # Default initial screen

        def add_widget(self, screen):
            super().add_widget(screen)
            if screen.name:  # Check for name attribute
                self._screens[screen.name] = screen
            screen.manager = self  # Set the manager attribute on the screen

        def has_screen(self, name):
            return name in self._screens

        def get_screen(self, name):
            return self._screens.get(name)

        @property
        def current(self):
            return self._current

        @current.setter
        def current(self, value):
            self._current = value

    sys.modules["kivy.uix.screenmanager"] = MagicMock(ScreenManager=MockScreenManager, Screen=MockScreen)
    sys.modules["kivy.graphics"] = MagicMock()
    sys.modules["kivy.core.text"] = MagicMock()
    sys.modules["kivy.core.window"] = MagicMock(Window=MagicMock(width=800, height=600))
    sys.modules["kivy.metrics"] = MagicMock(sp=lambda x: x)  # Mock sp to return the value itself
