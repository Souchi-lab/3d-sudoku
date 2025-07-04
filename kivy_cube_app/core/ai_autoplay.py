
import csv
import sys
import os
import time
import uuid

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from kivy_cube_app.core.cube_logic import CubeLogic
from kivy_cube_app.core.field_adapter import FieldAdapter
from kivy_cube_app.core.game_state import GameState
from kivy_cube_app.core.cpu_player import CpuPlayer
import logging
from kivy_cube_app.utils.logger import AppLogger

class AutoPlayBot:
    def __init__(self, n, level, app_logger):
        self.n = n
        self.level = level
        self.field = FieldAdapter(N=self.n)
        self.logic = CubeLogic(self.field, N=self.n)
        self.game_state = GameState(N=self.n, level=self.level)
        self.cpu_player = CpuPlayer(self.logic, self.field, N=self.n)
        self.logger = app_logger.get_logger()

    def run_game(self):
        start_time = time.time()
        
        self.logger.info("--- Game Start ---")

        while not self.game_state.is_game_over(self.logic):
            current_number = self.game_state.current_number
            
            if not self.cpu_player.make_move(current_number):
                self.logger.info(f"CPU could not make a move for number {current_number}.")
                # CPUが手を打てなかった場合
                if not self.logic.can_place_number(current_number):
                    self.logger.info(f"Number {current_number} cannot be placed anywhere. Game Over.")
                    # 現在の数字がどこにも配置できない場合、ゲームオーバー
                    break
                elif self.game_state.can_skip():
                    self.logger.info(f"Skipping turn for number {current_number}.")
                    # 配置は可能だがCPUが手を見つけられなかった場合、プレイヤーをスキップ
                    self.game_state.skip_turn()
                else:
                    self.logger.info(f"Cannot skip turn for number {current_number}. Game Over.")
                    # スキップもできない場合、ゲームオーバー
                    break
            
            self.game_state.next_turn()

        end_time = time.time()
        clear_time = end_time - start_time
        score = self.game_state.get_score(1) # Player 1のスコアを取得

        self.logger.info("--- Game End Board ---")
        self._log_board()
        
        return clear_time, score

    def _log_board(self):
        board = self.field.get_all_numbers()
        for z in range(self.n):
            self.logger.info(f"Layer Z={z+1}")
            for y in range(self.n):
                row_str = " ".join([str(board[x][y][z]) for x in range(self.n)])
                self.logger.info(f"  {row_str}")

def main():
    results = []
    app_logger_instance = AppLogger() # Get AppLogger instance
    logger = app_logger_instance.get_logger() # Get logger object from instance
    # for n in range(3, 6):
    for n in range(3, 6):
        for i in range(1):
            game_id = str(uuid.uuid4())
            app_logger_instance.set_game_id(game_id)
            logger.info(f"Setting game ID: {game_id}")
            print(f"Running game for N={n}, iteration {i+1}, Game ID: {game_id}")
            # Assuming level is tied to N for now
            level = n - 2 # Simple mapping for level
            bot = AutoPlayBot(n=n, level=level, app_logger=app_logger_instance)
            
            # Game Start Board logging should be inside run_game
            clear_time, score = bot.run_game()
            results.append([n, i+1, clear_time, score])

    with open('autoplay_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['N', 'Iteration', 'Clear Time', 'Score'])
        writer.writerows(results)

if __name__ == '__main__':
    main()
