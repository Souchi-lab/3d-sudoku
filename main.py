import os

from kivy.app import App
from kivy.metrics import sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy_cube_app.services.game_controller import GameController
from kivy_cube_app.ui.cube_view import Cube3DWidget
from kivy_cube_app.ui.rule_screen import RuleExplanationPopup


class LevelSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", spacing=sp(10), padding=sp(20))

        title = Label(text="Select Level", font_size=sp(32), size_hint_y=0.2)
        layout.add_widget(title)

        levels_box = BoxLayout(orientation="vertical", spacing=sp(5), size_hint_y=0.8)
        for level in range(1, 6):  # Levels 1 to 5
            btn = Button(text=f"Level {level}", font_size=sp(24))
            btn.bind(on_press=lambda _, level_num=level: self.select_level(level_num))
            levels_box.add_widget(btn)

        layout.add_widget(levels_box)
        self.add_widget(layout)

    def select_level(self, level):
        self.manager.get_screen("game").start_game(level)
        self.manager.current = "game"


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = None
        self.cube_widget = None

    def start_game(self, level):
        # Clear previous widgets if any
        self.clear_widgets()

        layout = BoxLayout(orientation="vertical", padding=0, spacing=0)
        os.makedirs("log", exist_ok=True)

        # --- Status Bar (Score, Turn, Timer) ---
        self.status_bar = BoxLayout(size_hint_y=None, height=sp(40), padding=(sp(10), 0))
        self.score_label = Label(font_size=sp(18), color=(1, 1, 1, 1), halign="left", valign="middle")
        self.turn_label = Label(font_size=sp(20), color=(1, 1, 1, 1), bold=True)
        self.time_label = Label(font_size=sp(18), color=(1, 1, 1, 1), halign="right", valign="middle")
        self.score_label.bind(size=self.score_label.setter("text_size"))
        self.time_label.bind(size=self.time_label.setter("text_size"))

        self.status_bar.add_widget(self.score_label)
        self.status_bar.add_widget(self.turn_label)
        self.status_bar.add_widget(self.time_label)
        layout.add_widget(self.status_bar)

        # --- Game Controller and Cube Widget ---
        from kivy_cube_app.utils.constants import N_VALUE

        self.controller = GameController(self, is_ta_mode=True, level=level, N=N_VALUE)
        initial_hints = self.controller.get_initial_filled()
        self.controller.log_board()

        self.cube_widget = Cube3DWidget(
            logic=self.controller.logic,
            get_current_number_fn=lambda: self.controller.state.current_number,
            get_upcoming_fn=lambda cnt=None: self.controller.state.get_upcoming(cnt),
            initial_filled=initial_hints,
        )
        layout.add_widget(self.cube_widget)

        self.controller.set_cube_callbacks(self.cube_widget)
        self.controller.set_timer_update_callback(self.update_time)
        self.controller.set_score_update_callback(self.update_status)

        # --- Bottom Buttons ---
        reset_btn = Button(text="RESET", size_hint_y=None, height=sp(45), font_size=sp(18))
        reset_btn.bind(on_press=lambda _: self.controller.reset_game())

        rule_btn = Button(text="RULES", size_hint_y=None, height=sp(45), font_size=sp(18))
        rule_btn.bind(on_press=lambda _: RuleExplanationPopup().open())

        back_btn = Button(text="< LEVEL SELECT", size_hint_y=None, height=sp(45), font_size=sp(18))
        back_btn.bind(on_press=self.go_to_level_select)

        button_layout = BoxLayout(size_hint_y=None, height=sp(50), spacing=sp(5))
        button_layout.add_widget(back_btn)
        button_layout.add_widget(reset_btn)
        button_layout.add_widget(rule_btn)
        layout.add_widget(button_layout)

        self.add_widget(layout)
        self.update_status()  # Initial status update

    def update_status(self):
        if not self.controller:
            return
        p1 = self.controller.state.players[1]
        p2 = self.controller.state.players[2]
        current_player = self.controller.state.get_current_player()
        n = self.controller.state.current_number

        self.score_label.text = f"P1: {p1.score}  P2: {p2.score}"
        self.turn_label.text = f"Turn: {current_player.name} ({n})"

        if current_player.id == 1:
            self.turn_label.color = (1, 0.8, 0.8, 1)
        else:
            self.turn_label.color = (0.8, 0.8, 1, 1)

    def update_time(self, elapsed_seconds):
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)
        self.time_label.text = f"Time: {minutes:02d}:{seconds:02d}"

    def go_to_level_select(self, instance):
        if self.controller:
            self.controller.stop_game()  # Stop timer etc.
        self.manager.current = "level_select"


class SudokuApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LevelSelectScreen(name="level_select"))
        sm.add_widget(GameScreen(name="game"))
        return sm


if __name__ == "__main__":
    SudokuApp().run()
