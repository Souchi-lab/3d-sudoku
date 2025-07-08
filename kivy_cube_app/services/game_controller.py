import uuid
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.clock import Clock # Import Clock

from ..core.game_state import GameState
from ..core.field_adapter import FieldAdapter
from ..core.cube_logic import CubeLogic
from ..core.cpu_player import CpuPlayer
from ..utils.constants import CPU_PLAYER_ID
from ..utils.logger import AppLogger

class GameController:
    def __init__(self, root_widget, is_ta_mode: bool = False, level: int = 1, N: int = 3):
        self.root = root_widget
        
        # --- Logger setup --
        self.app_logger_instance = AppLogger(log_lv=2)
        self.logger = self.app_logger_instance.get_logger()
        game_id = str(uuid.uuid4())
        self.app_logger_instance.set_game_id(game_id)
        self.logger.info(f"New Game Start. Game ID: {game_id}")

        self.state = GameState(is_ta_mode=is_ta_mode, level=level, N=N)
        self.field = FieldAdapter(N=N)
        self.logic = CubeLogic(self.field, N=N, initial_data=self.state.initial_filled_cells)
        self.cpu_player = CpuPlayer(self.logic, self.field, N=N)
        self._timer_update_callback = None # New property
        self._score_update_callback = None # New property for score/status updates
        self._number_skip_notification_callback = None # New property for number skip notification
        Clock.schedule_interval(self._update_timer, 1) # Schedule timer update
        self.state.set_number_skip_callback(self._on_number_skipped)
        # self.log_board()

    def log_board(self):
        board = self.field.get_all_numbers()
        for z in range(self.state.N):
            self.logger.info(f"Layer Z={z+1}")
            for y in range(self.state.N):
                row_str = " ".join([str(board[x][y][z]) for x in range(self.state.N)])
                self.logger.info(f"  {row_str}")

    def set_cube_callbacks(self, cube_widget):
        cube_widget.set_on_success_input(self.on_success_input)
        cube_widget.set_number_skip_notification_callback(self._on_number_skipped)

    def set_timer_update_callback(self, callback_fn):
        self._timer_update_callback = callback_fn

    def set_score_update_callback(self, callback_fn):
        self._score_update_callback = callback_fn

    def set_number_skip_notification_callback(self, callback_fn):
        self._number_skip_notification_callback = callback_fn

    def _on_number_skipped(self, skipped_number):
        if self._number_skip_notification_callback:
            self._number_skip_notification_callback(skipped_number)

    def _update_timer(self, dt):
        self.state.update_timer()
        if self._timer_update_callback:
            self._timer_update_callback(self.state.get_elapsed_time())

    def get_initial_filled(self):
        return self.state.initial_filled_cells

    def on_success_input(self):
        self.state.add_score(self.state.current_number)
        self.state.next_turn()
        if self._score_update_callback:
            self._score_update_callback() # Call the score update callback
        if self.state.is_game_over(self.logic):
            self.show_game_over_popup()
        else:
            # If the game is not over, check if it's CPU's turn
            if self.state.current_player_id == CPU_PLAYER_ID:
                self._handle_cpu_turn()

        if self._timer_update_callback:
            self._timer_update_callback(self.state.get_elapsed_time()) # Update timer after successful input

    def _handle_cpu_turn(self):
        # CPU makes a move
        self.cpu_player.make_move(self.state.current_number)
        self.state.next_turn() # Add this line to switch to the next player
        # After CPU makes a move, check if the game is over again
        if self.state.is_game_over(self.logic):
            self.show_game_over_popup()
        else:
            # If game is not over, update score/status for the next player
            if self._score_update_callback:
                self._score_update_callback()

    def show_game_over_popup(self):
        p1_score = self.state.players[1].score
        p2_score = self.state.players[2].score
        winner = "Draw"
        if p1_score > p2_score:
            winner = self.state.players[1].name
        elif p2_score > p1_score:
            winner = self.state.players[2].name

        popup_content = BoxLayout(orientation='vertical')
        popup_content.add_widget(Label(text=f'Winner: {winner}\n\nP1: {p1_score} - P2: {p2_score}'))

        btn_layout = BoxLayout(size_hint_y=None, height='40dp')
        reset_btn = Button(text='Reset')
        reset_btn.bind(on_release=lambda x: (popup.dismiss(), self.reset_game()))
        exit_btn = Button(text='Exit')
        exit_btn.bind(on_release=lambda x: App.get_running_app().stop())
        btn_layout.add_widget(reset_btn)
        btn_layout.add_widget(exit_btn)
        popup_content.add_widget(btn_layout)

        popup = Popup(title='Game Over',
                      content=popup_content,
                      size_hint=(0.6, 0.4))
        popup.open()

    def reset_game(self):
        self.field.reset()
        self.logic.reset()
        self.state.reset_game(N=self.state.N, is_ta_mode=self.state.is_ta_mode, level=self.state.level)
        self.root.cube_widget.redraw()
        self.root.cube_widget.redraw_info()
        if self._timer_update_callback:
            self._timer_update_callback(self.state.get_elapsed_time()) # Reset timer display
        self.root.update_status()