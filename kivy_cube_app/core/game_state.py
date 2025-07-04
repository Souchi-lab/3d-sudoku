import random
from time import time
from ..utils.constants import TA_BASE_TIME_LV1, TA_BASE_TIME_LV2, TA_BASE_TIME_LV3, TA_BASE_TIME_LV4, TA_BASE_TIME_LV5, TIME_GAIN_LINE_COMPLETE, TIME_GAIN_SLICE_COMPLETE, TIME_GAIN_5_CONSECUTIVE_SUCCESS, TIME_PENALTY_WRONG_PLACEMENT, MAX_SKIP_COUNT
from ..core.scramble import scramble_board # Import scramble_board
from ..utils.logger import AppLogger

class Player:
    def __init__(self, player_id, name="Player"):
        self.id = player_id
        self.name = name
        self.score = 0
        self.consecutive_successes = 0 # 連続成功回数

    def add_score(self, value=1):
        self.score += value

    def reset_score(self):
        self.score = 0
        self.consecutive_successes = 0

class GameState:
    def __init__(self, N: int, is_ta_mode: bool = False, level: int = 1):
        self.logger = AppLogger().get_logger()
        self.N = N # Nをインスタンス変数として保持
        self.is_ta_mode = is_ta_mode
        self.level = level

        # プレイヤー情報初期化
        self.players = {
            1: Player(1, "Player 1"),
            2: Player(2, "Player 2")
        }
        self.current_player_id = 1

        # 初期配置の生成
        self.initial_filled_cells = self._generate_initial_filled_cells(self.level)

        # 数値シーケンスを最初に生成
        self.sequence = self.create_nums(self.initial_filled_cells)
        self.current_index = 0
        self.current_number = self.sequence[self.current_index]

        # タイマー関連
        self.time_left = 0.0
        self.last_update_time = 0.0 # New: Track last update time for accurate time calculation
        self.skip_count = 0
        self._number_skip_callback = None # New: Callback for number skip notification
        if self.is_ta_mode:
            self.start_timer(level)

    def _generate_initial_filled_cells(self, level: int) -> list:
        """
        レベルに基づいて初期配置セルを生成する。
        """
        # 解決済みのボードを生成
        solved_board = scramble_board(None, self.N)

        # レベルに応じたヒントの数を決定
        # 例: レベル1はヒントが多い、レベル5はヒントが少ない
        hint_counts = {
            1: 20, # Easy
            2: 15,
            3: 10,
            4: 7,
            5: 5,  # Hard
        }
        num_hints = hint_counts.get(level, 10) # Default to 10 hints

        all_possible_positions = []
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    all_possible_positions.append([i, j, k])

        random.shuffle(all_possible_positions)

        hints = []
        for pos in all_possible_positions[:num_hints]:
            i, j, k = pos
            hints.append({"pos": pos, "value": solved_board[i][j][k]})
        # self.logger.info(f"Generated {len(hints)} hints: {hints}")
        return hints

    def create_nums(self, initial_filled_cells: list) -> list:
        """
        ゲーム開始時に、各数字（1〜N）を N² 個ずつ用意し、
        全体で N³ の数列を作ってシャッフルする
        """
        from random import shuffle

        count_per_number = self.N ** 2
        _nums = [n for n in range(1, self.N + 1)
                for _ in range(count_per_number)]

        # Remove the numbers that are already placed on the board
        for cell in initial_filled_cells:
            if cell['value'] in _nums:
                _nums.remove(cell['value'])

        shuffle(_nums)
        return _nums

    def next_turn(self):
        # プレイヤーを交代
        self.current_player_id = 2 if self.current_player_id == 1 else 1

        # 現在の数値をシーケンスから削除
        # current_indexが指す要素を削除
        if self.sequence and self.current_index < len(self.sequence):
            self.sequence.pop(self.current_index)

        # シーケンスの次の数値へ
        if self.sequence:
            # current_indexはpopによって自動的に調整されるが、
            # シーケンスの長さを超えないように調整
            self.current_index = min(self.current_index, len(self.sequence) - 1)
            self.current_number = self.sequence[self.current_index]
        else:
            self.current_number = None # シーケンスが空になった場合

    def get_upcoming(self, count=None) -> list:
        """
        現在インデックス以降のシーケンスを返す。
        count指定で先頭count個、Noneなら全て返す
        """
        rem = self.sequence[self.current_index:]
        return rem[:count] if count is not None else rem

    def add_score(self, value=1):
        self.players[self.current_player_id].add_score(value)

    def get_score(self, player_id):
        return self.players[player_id].score

    def get_current_player(self):
        return self.players[self.current_player_id]

    def reset_game(self, N: int, is_ta_mode: bool = False, level: int = 1):
        self.N = N
        self.is_ta_mode = is_ta_mode
        self.level = level

        # スコア・ターン・シーケンスをリセット
        for p in self.players.values():
            p.reset_score()
        self.current_player_id = 1

        # 初期配置の再生成
        self.initial_filled_cells = self._generate_initial_filled_cells(self.level)

        self.sequence = self.create_nums(self.initial_filled_cells)
        self.current_index = 0
        self.current_number = self.sequence[self.current_index]

        # タイマーリセット
        self.time_left = 0.0
        self.last_update_time = 0.0
        if self.is_ta_mode:
            self.start_timer(level)

    def is_game_over(self, cube_logic) -> bool:
        # 全てのセルが埋まったかどうか
        all_cells_filled = all(cube_logic.get_number(i, j, k) is not None
                               for i in range(self.N)
                               for j in range(self.N)
                               for k in range(self.N))

        # 現在の数字を置ける場所が全くない場合
        no_valid_placement = not cube_logic.can_place_number(self.current_number)

        # TAモードの場合、時間切れもゲームオーバー条件に含める
        if self.is_ta_mode:
            return all_cells_filled or self.is_time_up() or no_valid_placement
        else:
            return all_cells_filled or no_valid_placement

    # --- タイマー関連メソッド ---
    def start_timer(self, level: int):
        from time import time
        base_times = {
            1: TA_BASE_TIME_LV1,
            2: TA_BASE_TIME_LV2,
            3: TA_BASE_TIME_LV3,
            4: TA_BASE_TIME_LV4,
            5: TA_BASE_TIME_LV5,
        }
        self.time_left = float(base_times.get(level, 600)) # デフォルトは600秒
        self.last_update_time = time() # Initialize last_update_time

    def update_timer(self):
        from time import time
        if self.is_ta_mode:
            current_time = time()
            elapsed_since_last_update = current_time - self.last_update_time
            self.time_left -= elapsed_since_last_update
            self.last_update_time = current_time

    def get_elapsed_time(self) -> float:
        """現在の残り時間を返す"""
        return max(0.0, self.time_left)

    def add_time(self, amount: float):
        if self.is_ta_mode:
            self.time_left += amount

    def subtract_time(self, amount: float):
        if self.is_ta_mode:
            self.time_left -= amount

    def is_time_up(self) -> bool:
        if self.is_ta_mode:
            return self.time_left <= 0
        return False

    def can_skip(self) -> bool:
        return self.skip_count < MAX_SKIP_COUNT

    def skip_turn(self):
        if self.can_skip():
            self.skip_count += 1
            if self.is_ta_mode:
                self.subtract_time(30)
                self.add_score(-20)
            else:
                self.add_score(-20)
            self.next_turn()

    def set_number_skip_callback(self, callback_fn):
        self._number_skip_callback = callback_fn

    def next_number_only(self):
        """
        プレイヤーを交代させずに、シーケンスの次の数値に進めます。
        """
        self.current_index = (self.current_index + 1) % len(self.sequence)
        self.current_number = self.sequence[self.current_index]
        if self._number_skip_callback:
            self._number_skip_callback(self.current_number)
  