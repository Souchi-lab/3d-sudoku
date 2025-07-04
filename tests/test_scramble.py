import unittest
import random
from kivy_cube_app.core.scramble import scramble_board

class TestScramble(unittest.TestCase):

    def setUp(self):
        # N=3の完成盤テンプレート
        self.base_board_N3 = [
            [ # X=0
                [1, 2, 3], # Y=0
                [2, 3, 1], # Y=1
                [3, 1, 2]  # Y=2
            ],
            [ # X=1
                [3, 1, 2],
                [1, 2, 3],
                [2, 3, 1]
            ],
            [ # X=2
                [2, 3, 1],
                [3, 1, 2],
                [1, 2, 3]
            ]
        ]

    def test_scramble_board_basic_N3(self):
        N = 3
        scrambled_board = scramble_board(self.base_board_N3, N)

        # 盤面のサイズが正しいことを確認
        self.assertEqual(len(scrambled_board), N)
        self.assertEqual(len(scrambled_board[0]), N)
        self.assertEqual(len(scrambled_board[0][0]), N)

        # 全てのセルがNoneでないことを確認
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    self.assertIsNotNone(scrambled_board[i][j][k])

        # 数字の範囲が正しいことを確認 (1からN)
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    self.assertGreaterEqual(scrambled_board[i][j][k], 1)
                    self.assertLessEqual(scrambled_board[i][j][k], N)

    def test_scramble_board_reproducibility_with_seed(self):
        N = 3
        seed = 42

        scrambled_board1 = scramble_board(self.base_board_N3, N, seed=seed)
        scrambled_board2 = scramble_board(self.base_board_N3, N, seed=seed)

        # 同じシードで同じ結果になることを確認
        self.assertEqual(scrambled_board1, scrambled_board2)

        # 異なるシードで異なる結果になることを確認 (ランダム性が十分であれば)
        scrambled_board3 = scramble_board(self.base_board_N3, N, seed=seed + 1)
        self.assertNotEqual(scrambled_board1, scrambled_board3)

    def test_scramble_board_N_variable(self):
        # N=2のテスト (簡略化のため)
        base_board_N2 = [
            [[1, 2],
             [2, 1]],
            [[2, 1],
             [1, 2]]
        ]
        N = 2
        scrambled_board_N2 = scramble_board(base_board_N2, N)
        self.assertEqual(len(scrambled_board_N2), N)
        self.assertEqual(len(scrambled_board_N2[0]), N)
        self.assertEqual(len(scrambled_board_N2[0][0]), N)

        # N=4のテスト (簡略化のため、ここではサイズのみ確認)
        base_board_N4 = [[[1 for _ in range(4)] for _ in range(4)] for _ in range(4)] # ダミーデータ
        N = 4
        scrambled_board_N4 = scramble_board(base_board_N4, N)
        self.assertEqual(len(scrambled_board_N4), N)
        self.assertEqual(len(scrambled_board_N4[0]), N)
        self.assertEqual(len(scrambled_board_N4[0][0]), N)

if __name__ == '__main__':
    unittest.main()
