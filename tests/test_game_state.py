import os
import random
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivy_cube_app.core.game_state import GameState
from kivy_cube_app.utils.constants import LENGTH_OF_SIDE, MAX_SKIP_COUNT, TA_BASE_TIME_LV1


class TestGameState(unittest.TestCase):
    @patch("kivy_cube_app.core.game_state.GameState._generate_initial_filled_cells", return_value=[])
    def test_initial_state(self, mock_generate_initial_filled_cells):
        gs = GameState(N=LENGTH_OF_SIDE)
        self.assertEqual(gs.current_player_id, 1)
        self.assertEqual(len(gs.sequence), LENGTH_OF_SIDE**3)
        self.assertEqual(gs.current_index, 0)
        self.assertEqual(gs.players[1].score, 0)
        self.assertEqual(gs.players[2].score, 0)
        mock_generate_initial_filled_cells.assert_called_once_with(1)  # Default level is 1

    def test_create_nums_hint_exclusion(self):
        # GS-CN-01: ヒント除外
        gs = GameState(N=LENGTH_OF_SIDE)
        initial_filled_cells = [{"pos": [0, 0, 0], "value": 1}, {"pos": [0, 0, 1], "value": 2}]
        # Get initial counts before creating nums
        initial_count_1 = LENGTH_OF_SIDE**2
        initial_count_2 = LENGTH_OF_SIDE**2

        nums = gs.create_nums(initial_filled_cells)
        # 期待される長さは N^3 からヒントの数だけ減る
        self.assertEqual(len(nums), LENGTH_OF_SIDE**3 - len(initial_filled_cells))
        # ヒントとして除外された値の数が正しく減っていることを確認
        self.assertEqual(nums.count(1), initial_count_1 - 1)
        self.assertEqual(nums.count(2), initial_count_2 - 1)

    def test_create_nums_shuffle_reproducibility(self):
        # GS-CN-02: シャッフル再現
        seed = 42
        initial_filled_cells = []

        gs1 = GameState(N=LENGTH_OF_SIDE)
        random.seed(seed)
        nums1 = gs1.create_nums(initial_filled_cells)

        gs2 = GameState(N=LENGTH_OF_SIDE)
        random.seed(seed)
        nums2 = gs2.create_nums(initial_filled_cells)

        self.assertEqual(nums1, nums2)

    def test_next_turn(self):
        gs = GameState(N=LENGTH_OF_SIDE)
        initial_player = gs.current_player_id
        initial_index = gs.current_index
        gs.next_turn()
        self.assertNotEqual(gs.current_player_id, initial_player)
        self.assertEqual(
            gs.current_index, initial_index
        )  # current_indexはpopによって自動的に調整されるため、同じになる

    def test_next_turn_sequence_shortens(self):
        # GS-NT-02: シーケンス短縮
        gs = GameState(N=LENGTH_OF_SIDE)
        initial_len = len(gs.sequence)
        gs.next_turn()
        self.assertEqual(len(gs.sequence), initial_len - 1)

    def test_get_upcoming(self):
        gs = GameState(N=LENGTH_OF_SIDE)
        upcoming = gs.get_upcoming()
        self.assertEqual(len(upcoming), len(gs.sequence))
        upcoming_5 = gs.get_upcoming(5)
        self.assertEqual(len(upcoming_5), 5)

    def test_add_score(self):
        gs = GameState(N=LENGTH_OF_SIDE)
        gs.add_score(5)
        self.assertEqual(gs.players[1].score, 5)
        gs.next_turn()
        gs.add_score(3)
        self.assertEqual(gs.players[2].score, 3)

    def test_skip_turn(self):
        # GS-SK-01: スコア減算 & ターン
        gs = GameState(N=LENGTH_OF_SIDE)
        initial_score = gs.get_score(gs.current_player_id)
        initial_player_id = gs.current_player_id
        initial_skip_count = gs.skip_count

        gs.skip_turn()

        # スコアが減算されたことを確認
        self.assertEqual(gs.get_score(initial_player_id), initial_score - 20)
        # プレイヤーが交代したことを確認
        self.assertNotEqual(gs.current_player_id, initial_player_id)
        # スキップカウントが増加したことを確認
        self.assertEqual(gs.skip_count, initial_skip_count + 1)

    def test_skip_turn_max_skip_count(self):
        # MAX_SKIP_COUNTまでスキップできることを確認
        gs = GameState(N=LENGTH_OF_SIDE)
        for _ in range(MAX_SKIP_COUNT):
            self.assertTrue(gs.can_skip())
            gs.skip_turn()
        self.assertFalse(gs.can_skip())
        # MAX_SKIP_COUNTを超えてスキップしようとしても、スキップされないことを確認
        initial_score = gs.get_score(gs.current_player_id)
        initial_player_id = gs.current_player_id
        initial_skip_count = gs.skip_count
        gs.skip_turn()
        self.assertEqual(gs.get_score(initial_player_id), initial_score)
        self.assertEqual(gs.current_player_id, initial_player_id)
        self.assertEqual(gs.skip_count, initial_skip_count)

    @patch("kivy_cube_app.core.game_state.time")
    def test_timer_expiration(self, mock_time):
        # GS-TM-01: 期限切れ
        # 初期時間設定
        initial_time = 100.0
        mock_time.return_value = initial_time  # 最初のtime()呼び出し（GameState.__init__内）用

        gs = GameState(N=LENGTH_OF_SIDE, is_ta_mode=True, level=1)
        # 時間が経過し、期限切れになるように設定
        time_after_expiration = initial_time + gs.time_left + 1.0  # 1秒オーバー
        mock_time.return_value = time_after_expiration  # 2回目のtime()呼び出し（gs.update_timer()内）用

        gs.update_timer()
        self.assertTrue(gs.is_time_up())

    def test_is_game_over_all_cells_filled(self):
        # GS-GO-01: 完成盤面
        gs = GameState(N=LENGTH_OF_SIDE)
        mock_cube_logic = MagicMock()
        # all_cells_filled が True を返すように設定
        mock_cube_logic.all_cells_filled.return_value = True
        mock_cube_logic.can_place_number.return_value = True  # 配置可能でもゲームオーバーになることを確認

        self.assertTrue(gs.is_game_over(mock_cube_logic))

    def test_is_game_over_no_valid_placement(self):
        # GS-GO-02: 配置不能
        gs = GameState(N=LENGTH_OF_SIDE)
        mock_cube_logic = MagicMock()
        # all_cells_filled が False を返すように設定
        mock_cube_logic.all_cells_filled.return_value = False
        # 配置可能な場所がないと仮定
        mock_cube_logic.can_place_number.return_value = False

        self.assertTrue(gs.is_game_over(mock_cube_logic))

    def test_is_game_over_not_game_over(self):
        gs = GameState(N=LENGTH_OF_SIDE)
        mock_cube_logic = MagicMock()
        mock_cube_logic.all_cells_filled.return_value = False
        mock_cube_logic.can_place_number.return_value = True
        self.assertFalse(gs.is_game_over(mock_cube_logic))

    def test_reset_game(self):
        gs = GameState(N=LENGTH_OF_SIDE)
        gs.add_score(10)
        gs.next_turn()
        gs.reset_game(N=LENGTH_OF_SIDE)
        self.assertEqual(gs.current_player_id, 1)
        self.assertEqual(gs.current_index, 0)
        self.assertEqual(gs.players[1].score, 0)
        self.assertEqual(gs.players[2].score, 0)


if __name__ == "__main__":
    unittest.main()
